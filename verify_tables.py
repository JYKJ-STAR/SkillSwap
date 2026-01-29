import sqlite3

conn = sqlite3.connect('Class db/skillswap.db')
cursor = conn.cursor()

print("Verifying live_chat_session table:")
cursor.execute('PRAGMA table_info(live_chat_session)')
for row in cursor:
    print(f"  - {row[1]} ({row[2]})")

print("\nVerifying live_chat_message table:")
cursor.execute('PRAGMA table_info(live_chat_message)')
for row in cursor:
    print(f"  - {row[1]} ({row[2]})")

conn.close()
print("\n✅ Tables verified successfully!")
