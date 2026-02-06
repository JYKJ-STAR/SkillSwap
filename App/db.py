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
        # Challenge Table Migration for target_count
        cursor.execute("PRAGMA table_info(challenge)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'target_count' not in columns:
            print("🔄 Adding 'target_count' column to challenge table...")
            cursor.execute("ALTER TABLE challenge ADD COLUMN target_count INTEGER DEFAULT 1")
            conn.commit()
            print("✅ Database migration complete for challenge table (target_count)!")
        
        # Add admin_connected column to live_chat_session if it doesn't exist
        try:
            cursor.execute("PRAGMA table_info(live_chat_session)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'admin_connected' not in columns:
                print("🔄 Adding admin_connected column to live_chat_session...")
                cursor.execute("ALTER TABLE live_chat_session ADD COLUMN admin_connected INTEGER DEFAULT 0")
                conn.commit()
                print("✅ admin_connected column added!")
        except Exception as admin_conn_error:
            print(f"⚠️ Admin connection migration note: {admin_conn_error}")
        
        # Create live chat tables if they don't exist
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='live_chat_session'")
            if not cursor.fetchone():
                print("🔄 Creating live chat tables...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS live_chat_session (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        status TEXT DEFAULT 'active' CHECK (status IN ('active', 'closed')),
                        admin_connected INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS live_chat_message (
                        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        sender_type TEXT NOT NULL CHECK (sender_type IN ('user', 'admin', 'system')),
                        sender_id INTEGER,
                        message_text TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES live_chat_session (session_id) ON DELETE CASCADE
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session_user ON live_chat_session(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session_status ON live_chat_session(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_message_session ON live_chat_message(session_id)")
                conn.commit()
                print("✅ Live chat tables created!")
        except Exception as chat_error:
            print(f"⚠️ Chat migration note: {chat_error}")
        
        # Create user_challenge table for proof submissions
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_challenge'")
            if not cursor.fetchone():
                print("🔄 Creating user_challenge table...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_challenge (
                        user_challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        challenge_id INTEGER NOT NULL,
                        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
                        proof_file TEXT,
                        proof_description TEXT,
                        admin_comment TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (challenge_id) REFERENCES challenge(challenge_id) ON DELETE CASCADE
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_challenge_user ON user_challenge(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_challenge_challenge ON user_challenge(challenge_id)")
                conn.commit()
                print("✅ user_challenge table created!")
        except Exception as uc_error:
            print(f"⚠️ User challenge migration note: {uc_error}")
        
        # Add proof_description column to event_booking table
        cursor.execute("PRAGMA table_info(event_booking)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'proof_description' not in columns:
            print("🔄 Adding 'proof_description' column to event_booking table...")
            cursor.execute("ALTER TABLE event_booking ADD COLUMN proof_description TEXT")
            conn.commit()
            print("✅ Database migration complete for event_booking table!")
        
        # Add expiry_date column to reward_redemption table
        cursor.execute("PRAGMA table_info(reward_redemption)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'expiry_date' not in columns:
            print("🔄 Adding 'expiry_date' column to reward_redemption table...")
            cursor.execute("ALTER TABLE reward_redemption ADD COLUMN expiry_date TEXT")
            conn.commit()
            print("✅ Database migration complete for reward_redemption table!")

        conn.close()
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")

