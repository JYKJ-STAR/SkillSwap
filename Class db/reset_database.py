#!/usr/bin/env python3
"""
Database Reset Script
Deletes all users and creates 3 test users with known credentials
"""
import sqlite3
from werkzeug.security import generate_password_hash

# Database path
DB_PATH = 'Class db/skillswap.db'

# User credentials with fixed IDs
USERS = [
    {
        'id': 1,
        'name': 'Admin',
        'email': 'Admin@gmail.com',
        'password': 'Admin@1',
        'role': 'admin'
    },
    {
        'id': 2,
        'name': 'JaydenYip',
        'email': 'Jayden@gmail.com',
        'password': 'Jayden@1',
        'role': 'youth'
    },
    {
        'id': 3,
        'name': 'Dickson',
        'email': 'Dickson@gmail.com',
        'password': 'Dickson@1',
        'role': 'senior'
    }
]

def reset_database():
    """Reset database with test users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Delete all users and reset auto-increment counter
        cursor.execute("DELETE FROM user")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='user'")
        print("✓ Deleted all existing users and reset IDs")
        
        # Create users
        for user in USERS:
            password_hash = generate_password_hash(user['password'])
            cursor.execute(
                """INSERT INTO user (user_id, name, email, password_hash, role, verification_status)
                   VALUES (?, ?, ?, ?, ?, 'verified')""",
                (user['id'], user['name'], user['email'], password_hash, user['role'])
            )
            print(f"✓ Created {user['role']}: {user['email']} (ID: {user['id']})")
        
        conn.commit()
        print("\n✅ Database reset complete!")
        print("\nLogin Credentials:")
        print("-" * 50)
        for user in USERS:
            print(f"ID: {user['id']:<4} Email: {user['email']:<25} Password: {user['password']}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    reset_database()
