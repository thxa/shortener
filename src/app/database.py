import asyncpg
from fastapi import Request, Depends
from .config import settings

create_url_mappings_table_sql = """
        CREATE TABLE IF NOT EXISTS url_mappings (
                id SERIAL PRIMARY KEY,
                long_url TEXT NOT NULL UNIQUE,
                short_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
"""

async def init_tables(conn):
    await conn.execute(create_url_mappings_table_sql )


async def create_db_pool():
    return await asyncpg.create_pool(**settings.DB_CONFIG)

async def close_db_pool(pool):
    await pool.close()

async def get_db_pool(request: Request):
    return request.state.db_pool

async def get_db_connection(pool=Depends(get_db_pool)):
    async with pool.acquire() as conn:
        await init_tables(conn)
        yield conn
