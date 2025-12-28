import sqlite3
import os

DATABASE = os.path.join('Class db', 'skillswap.db')
SCHEMA_FILE = os.path.join('Class db', 'schema.sql')
SEED_FILE = os.path.join('Class db', 'seed.sql')

def init_db():
    if os.path.exists(DATABASE):
        print(f"Removing existing {DATABASE}...")
        os.remove(DATABASE)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Enable Foreign Keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("Executing schema.sql...")
    with open(SCHEMA_FILE, 'r') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    print("Executing seed.sql...")
    with open(SEED_FILE, 'r') as f:
        seed_sql = f.read()
        cursor.executescript(seed_sql)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
