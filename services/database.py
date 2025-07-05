import sqlite3
import os
from config import SQLITE_DB_PATH

def get_db_connection():
    """
    Returns a new SQLite database connection using the configured database path.
    
    Returns:
        sqlite3.Connection: SQLite connection object.
    """
    return sqlite3.connect(SQLITE_DB_PATH)

def ensure_tables():
    """
    Ensures that the required tables ('users' and 'modules') exist in the database.
    Creates them if they do not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        username TEXT,
        registration_date TEXT,
        is_active INTEGER DEFAULT 1
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS modules (
        module_id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_name TEXT,
        course_run_id TEXT,
        course_run_code TEXT,
        attendance_url TEXT,
        qr_code_url TEXT,
        start_date TEXT,
        end_date TEXT
    )''')
    
    conn.commit()
    cursor.close()
    conn.close()

def cleanup_duplicate_telegram_ids():
    """
    Removes duplicate Telegram user IDs from the 'users' table, keeping only the latest entry for each Telegram ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete all but the latest user_id for each telegram_id
    cursor.execute('''
        DELETE FROM users
        WHERE user_id NOT IN (
            SELECT MAX(user_id) FROM users GROUP BY telegram_id
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
