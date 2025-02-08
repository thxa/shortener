import uvicorn

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from contextlib import asynccontextmanager

import redis.asyncio as redis
import asyncpg

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter




HOST_NAME = "127.0.0.1:8000/"


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_connection)
    db_pool = await asyncpg.create_pool(user='postgres', password='fastapi', database='postgres', host='127.0.0.1')
    yield {"db_pool": db_pool}
    await FastAPILimiter.close()
    await db_pool.close()


async def get_database(request: Request):
   yield request.state.db_pool

async def get_db_connection(pool: asyncpg.pool.Pool = Depends(get_database)):
   async with pool.acquire() as connection:
      yield connection


app = FastAPI(lifespan=lifespan)

rate_limit = RateLimiter(times=1, seconds=10 * 60)


class Shortener(BaseModel):
    long_url: HttpUrl


def base62_encode(number):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    base62 = []
    if number == 0:
        return chars[0]
    while number > 0:
        number, remainder = divmod(number, 62)
        base62.append(chars[remainder])
    return ''.join(reversed(base62))


async def clean_table(conn):
    await conn.execute('DELETE FROM url_mappings')

async def add_long_url(conn, long_url: str):
    await conn.execute('INSERT INTO url_mappings(long_url) VALUES ($1)', (long_url))

async def get_last_id(conn):
    new_id = await conn.fetch('''SELECT currval('url_mappings_id_seq')''')  # Get the newly generated ID
    return new_id[0][0]
    
# Update the record with the short code
async def update_shortner(conn, short_code, new_id):
    await conn.execute('''UPDATE url_mappings SET short_code = $1 WHERE id = $2''', short_code, new_id)

async def retrieve_short_code_by_long_url(conn, long_url: str):
    return await conn.fetch('SELECT short_code FROM url_mappings WHERE long_url = $1', long_url)

async def retrieve_long_url_by_short_code(conn, short_code: str):
    return await conn.fetch('SELECT long_url FROM url_mappings WHERE short_code = $1', short_code)

async def generate_short_code(conn, long_url: str):
    # Check if the long URL already exists
    short_code = ""
    result = await retrieve_short_code_by_long_url(conn, long_url)
    if result != []:
        short_code = result[0]
        return short_code 

    await add_long_url(conn, long_url)
    last_id = await get_last_id(conn)
    
    short_code = base62_encode(last_id)
    await update_shortner(conn, short_code, last_id)
    return short_code


async def get_all(conn):
    values = await conn.fetch('SELECT long_url, short_code FROM url_mappings')
    return values






@app.post("/shorten/",  dependencies=[Depends(rate_limit)])
async def shorten(shortener: Shortener, conn=Depends(get_db_connection)):
    long_url = str(shortener.long_url)
    short_url = await generate_short_code(conn, long_url)
    return { "short_url" : f"{HOST_NAME}{short_url[0]}" }
        

@app.get("/{short_code}", dependencies=[Depends(rate_limit)])
async def get_short_url(short_code: str, conn=Depends(get_db_connection)):
    result = await retrieve_long_url_by_short_code(conn, short_code)
    if result == []:
        raise HTTPException(status_code=404, detail="Short url is not exist...") 
    long_url = result[0][0]
    return RedirectResponse(url=long_url, status_code=302)


@app.get("/api/urls")
async def short_codes(conn=Depends(get_db_connection)):
    short_codes_data = await get_all(conn)
    return [*map(lambda row:{row[0]:row[1]}, short_codes_data)]

@app.get("/", dependencies=[Depends(rate_limit)])
async def index():
    return {"msg": "Hello World"}



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
