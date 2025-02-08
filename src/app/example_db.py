import sqlite3
import contextlib

DATABASE_NAME = "shorturls.db"

def get_db():
    with contextlib.closing(sqlite3.connect(DATABASE_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            yield conn



def create_tables():
    conn = None
    with sqlite3.connect(DATABASE_NAME) as conn:
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS url_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                long_url TEXT NOT NULL UNIQUE,
                short_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        conn.execute(create_table_sql)


create_tables()

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


def generate_short_url(conn, long_url: str):
    conn = next(conn)
    # Check if the long URL already exists
    cur = conn.execute('SELECT short_code FROM url_mappings WHERE long_url = ?', (long_url,))
    existing = cur.fetchone()
    if existing:
        short_url = existing[0]
        return short_url

    # Insert the new URL (triggers auto-increment for `id`)
    cur = conn.execute('INSERT INTO url_mappings (long_url) VALUES (?)', (long_url,))
    new_id = cur.lastrowid  # Get the newly generated ID
    
    # Generate short code from the ID
    short_code = base62_encode(new_id)
    
    # Update the record with the short code
    cur.execute('''
        UPDATE url_mappings 
        SET short_code = ? 
        WHERE id = ?
    ''', (short_code, new_id))
    conn.commit()
    return short_code

def clean_table(conn):
    conn = next(conn)
    cur = conn.execute('DELETE FROM url_mappings')
    conn.commit()

conn = get_db()
clean_table(conn)
# for row in cur.fetchall():
#     print(row[0], row[1])


for i in range(1, 10):
    # print(base62_encode(i))
    test_long_url=f"https://google.com/{i}"
    conn = get_db()
    generate_short_url(conn, test_long_url)



conn = get_db()
cur = next(conn).execute('SELECT short_code, long_url FROM url_mappings')

for row in cur.fetchall():
    print(row[0], row[1])
# # breakpoint()
# # print(cur.fetchall())
# # print(generate_short_url(conn, "https://google.com/"))
