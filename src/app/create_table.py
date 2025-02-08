import asyncio
import asyncpg
import os
from config import settings 

create_table_sql = """
        CREATE TABLE IF NOT EXISTS url_mappings (
                id SERIAL PRIMARY KEY,
                long_url TEXT NOT NULL UNIQUE,
                short_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
"""
async def create_table(conn):
   await conn.execute(create_table_sql)

# print(DB_CONFIG)
# async def x (**kwargs):
#     print(kwargs)

async def run():
    conn = await asyncpg.connect(**settings.DB_CONFIG)
    # conn = await asyncpg.connect(user='postgres', password='fastapi',
    #                              database='postgres', host='127.0.0.1')

    # conn = await asyncpg.connect(**DB_CONFIG)
    await create_table(conn)
    print("Table Created")
    await conn.close()

asyncio.run(run())
