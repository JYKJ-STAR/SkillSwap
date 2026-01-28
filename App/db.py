import sqlite3
import os
from flask import g

# Validated absolute path to the database file in 'Class db' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, 'Class db', 'skillswap.db')

def get_db_connection():
    """Create and return a SQLite connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def close_db(e=None):
    """Close the database connection if it exists."""
    db = g.pop('db', None)

    if db is not None:
        db.close()

def migrate_database():
    """Run database migrations to add missing columns."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if published_at column exists
        cursor.execute("PRAGMA table_info(event)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'published_at' not in columns:
            print("🔄 Adding 'published_at' column to event table...")
            cursor.execute("ALTER TABLE event ADD COLUMN published_at TEXT")
            conn.commit()
            print("✅ Database migration complete for event table!")
            
        # Check if reply column exists in support_ticket table
        cursor.execute("PRAGMA table_info(support_ticket)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'reply' not in columns:
            print("🔄 Adding 'reply' column to support_ticket table...")
            cursor.execute("ALTER TABLE support_ticket ADD COLUMN reply TEXT")
            conn.commit()
            print("✅ Database migration complete for support_ticket table!")
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")

