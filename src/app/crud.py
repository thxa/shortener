from .utils import base62_encode

async def create_url_mapping(conn, long_url: str):
    await conn.execute('INSERT INTO url_mappings(long_url) VALUES ($1)', long_url)
    
async def get_last_id(conn):
    result = await conn.fetch("SELECT currval('url_mappings_id_seq')")
    return result[0][0]

async def update_short_code(conn, short_code: str, id: int):
    await conn.execute('UPDATE url_mappings SET short_code = $1 WHERE id = $2', short_code, id)

async def get_short_code(conn, long_url: str):
    result = await conn.fetch('SELECT short_code FROM url_mappings WHERE long_url = $1', long_url)
    return result[0][0] if result else None

async def get_long_url(conn, short_code: str):
    result = await conn.fetch('SELECT long_url FROM url_mappings WHERE short_code = $1', short_code)
    return result[0][0] if result else None

async def get_all_urls(conn):
    return await conn.fetch('SELECT long_url, short_code FROM url_mappings')

async def generate_short_code(conn, long_url: str):
    existing_code = await get_short_code(conn, long_url)
    if existing_code:
        return existing_code
    
    await create_url_mapping(conn, long_url)
    last_id = await get_last_id(conn)
    short_code = base62_encode(last_id)
    await update_short_code(conn, short_code, last_id)
    return short_code
