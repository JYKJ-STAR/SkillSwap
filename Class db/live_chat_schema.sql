-- Live Chat Tables

-- Chat sessions table
CREATE TABLE IF NOT EXISTS live_chat_session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active',  -- 'active', 'closed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS live_chat_message (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    sender_type TEXT NOT NULL,  -- 'user', 'admin', 'system'
    sender_id INTEGER,  -- user_id or admin_id (NULL for system messages)
    message_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES live_chat_session (session_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_session_user ON live_chat_session(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_session_status ON live_chat_session(status);
CREATE INDEX IF NOT EXISTS idx_chat_message_session ON live_chat_message(session_id);
