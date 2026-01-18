#!/usr/bin/env python3
"""
Database Reset Script
Deletes all users and creates 3 test users with known credentials
"""
import sqlite3
import argparse
from werkzeug.security import generate_password_hash

# Database path
DB_PATH = 'Class db/skillswap.db'

# User credentials with fixed IDs
USERS = [
    {
        'id': 1,
        'name': 'JaydenYip',
        'email': 'Jayden@gmail.com',
        'password': 'Jayden@1',
        'role': 'youth'
    },
    {
        'id': 2,
        'name': 'Dickson',
        'email': 'Dickson@gmail.com',
        'password': 'Dickson@1',
        'role': 'senior'
    }
]

# Admin users (minimal fields)
ADMIN_USERS = [
    {
        'name': 'Admin',
        'email': 'admin@email.com',
        'password': 'Admin@1',
        'photo': None,
        'privileged': 'Yes'
    }
]

def reset_users(cursor):
    """Reset users table"""
    # Delete all users and reset auto-increment counter
    cursor.execute("DELETE FROM user")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='user'")
    print("✓ Deleted all existing users and reset IDs")

    # Create regular users
    for user in USERS:
        password_hash = generate_password_hash(user['password'])
        cursor.execute(
            """INSERT INTO user (user_id, name, email, password_hash, role, verification_status)
               VALUES (?, ?, ?, ?, ?, 'verified')""",
            (user['id'], user['name'], user['email'], password_hash, user['role'])
        )
        print(f"✓ Created {user['role']}: {user['email']} (ID: {user['id']})")

def reset_admins(cursor):
    """Reset admins table"""
    # Delete all admins and reset auto-increment counter
    cursor.execute("DELETE FROM admin")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='admin'")
    print("✓ Deleted all existing admins and reset IDs")

    # Create admin users (minimal fields)
    for admin in ADMIN_USERS:
        password_hash = generate_password_hash(admin['password'])
        cursor.execute(
            """INSERT INTO admin (name, email, password_hash, photo, privileged)
               VALUES (?, ?, ?, ?, ?)""",
            (admin['name'], admin['email'], password_hash, admin['photo'], admin.get('privileged', 'No'))
        )
        print(f"✓ Created admin: {admin['email']} (Privileged: {admin.get('privileged', 'No')})")

def print_credentials():
    print("\nLogin Credentials:")
    print("-" * 50)
    for user in USERS:
        print(f"ID: {user['id']:<4} Email: {user['email']:<25} Password: {user['password']}")

def reset_database():
    """Reset database with test users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        reset_users(cursor)
        reset_admins(cursor)
        
        conn.commit()
        print("\n✅ Database reset complete!")
        print_credentials()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reset database tables.')
    parser.add_argument('--users', action='store_true', help='Reset users table only')
    parser.add_argument('--admins', action='store_true', help='Reset admins table only')
    # If no flags are provided, it will run default behavior (both)
    
    args = parser.parse_args()
    
    # Check if any specific flag was set
    if args.users or args.admins:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            if args.users:
                reset_users(cursor)
            if args.admins:
                reset_admins(cursor)
            
            conn.commit()
            print("\n✅ Selected tables reset complete!")
            if args.users:
                print_credentials()
        except Exception as e:
            conn.rollback()
            print(f"❌ Error: {e}")
        finally:
            conn.close()
    else:
        # Default behavior: Reset everything
        reset_database()
