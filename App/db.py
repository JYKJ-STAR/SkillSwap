import os
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Create and return a MySQL connection using .env settings."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise RuntimeError(f"Database connection failed: {e}")



        