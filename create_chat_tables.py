import sqlite3

# Connect to database
conn = sqlite3.connect('Class db/skillswap.db')
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT sql FROM sqlite_master WHERE name='live_chat_session'")
result = cursor.fetchone()

if result:
    print("Table 'live_chat_session' already exists:")
    print(result[0])
    print("\nDropping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS live_chat_message")
    cursor.execute("DROP TABLE IF EXISTS live_chat_session")
    conn.commit()
    print("✅ Old tables dropped")

print("\nCreating new tables...")

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS live_chat_session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS live_chat_message (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    sender_type TEXT NOT NULL,
    sender_id INTEGER,
    message_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES live_chat_session (session_id)
)
""")

# Create indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session_user ON live_chat_session(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session_status ON live_chat_session(status)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_message_session ON live_chat_message(session_id)")

conn.commit()
conn.close()

print("✅ Live chat tables created successfully!")
