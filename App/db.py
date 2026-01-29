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
        
        # Migrate challenge table to support 'pending' status
        # Check if the challenge table needs migration by trying to insert a pending row
        try:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='challenge'")
            table_sql = cursor.fetchone()
            if table_sql and "'pending'" not in table_sql[0]:
                print("🔄 Migrating 'challenge' table to support 'pending' status...")
                # Create new table with updated constraint
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS challenge_new (
                        challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'inactive', 'published', 'voided', 'ended')),
                        void_reason TEXT,
                        created_by INTEGER,
                        created_at TEXT NOT NULL DEFAULT (datetime('now')),
                        published_at TEXT,
                        voided_at TEXT,
                        ended_at TEXT,
                        FOREIGN KEY (created_by) REFERENCES admin(admin_id) ON DELETE SET NULL
                    )
                """)
                # Copy data from old table
                cursor.execute("INSERT INTO challenge_new SELECT * FROM challenge")
                # Drop old table
                cursor.execute("DROP TABLE challenge")
                # Rename new table
                cursor.execute("ALTER TABLE challenge_new RENAME TO challenge")
                conn.commit()
                print("✅ Challenge table migration complete!")
        except Exception as migration_error:
            print(f"⚠️ Challenge migration note: {migration_error}")
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")

