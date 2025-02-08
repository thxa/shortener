import asyncio
import asyncpg
import datetime

def base62_encode(number):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    base = 62
    base62 = []
    if number == 0:
        return chars[0]
    while number > 0:
        number, remainder = divmod(number, base)
        base62.append(chars[remainder])
        # base62.append(chars[number % base])
        # number //= base
    return ''.join(reversed(base62))

async def create_table(conn):
    create_table_sql = """
            CREATE TABLE IF NOT EXISTS url_mappings (
                    id SERIAL PRIMARY KEY,
                    long_url TEXT NOT NULL UNIQUE,
                    short_code TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
    """
    await conn.execute(create_table_sql)

async def clean_table(conn):
    await conn.execute('DELETE FROM url_mappings')

async def get_all(conn):
    values = await conn.fetch('SELECT * FROM url_mappings')
    return values

async def insert(conn, long_url):
    cur = await conn.execute('INSERT INTO url_mappings(long_url) VALUES ($1)', (long_url))

async def get_last_id(conn):
    new_id = await conn.fetch('''SELECT currval('url_mappings_id_seq')''')  # Get the newly generated ID
    return new_id[0][0]
    
async def update(conn, short_code, new_id):
    # Update the record with the short code
    await conn.execute('''UPDATE url_mappings SET short_code = $1 WHERE id = $2''', short_code, new_id)

async def get_long_url(conn, long_url):
    exisit = await conn.fetch('SELECT short_code FROM url_mappings WHERE long_url = $1', long_url)
    return exisit

async def generate_short_url(conn, long_url: str):
    # Check if the long URL already exists
    existing = await get_long_url(conn, long_url)
    if existing != []:
        short_code = existing[0]
        return short_code 

    await insert(conn, long_url)
    last_id = await get_last_id(conn)
    
    short_code = base62_encode(last_id)
    await update(conn, short_code, last_id)
    return short_code

async def run():
    conn = await asyncpg.connect(user='postgres', password='fastapi',
                                 database='postgres', host='127.0.0.1')
    # await clean_table(conn)

    # await get_all(conn)
    await create_table(conn)

    # await generate_short_url(conn, "https://google.com/helloworld32311")
    
    # # Generate short code from the ID
    # short_code = base62_encode(new_id)
    
    # # Update the record with the short code

    # values = await conn.fetch(
    #         'SELECT * FROM mytable WHERE id = $1',
    #         10,
    #         )

    # await get_all(conn)
    # print(values[0][3])
    await conn.close()

asyncio.run(run())
