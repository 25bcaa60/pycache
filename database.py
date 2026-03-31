"""
Database Module for Portfolio Website
Uses SQLite locally and Render Postgres in production when DATABASE_URL is set.
"""

import importlib
import os
import sqlite3
from urllib.parse import urlparse

try:
    pgdb = importlib.import_module('pg8000.dbapi')
except ImportError:
    pgdb = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DATABASE_NAME = os.path.join(BASE_DIR, 'portfolio.db')
RAW_DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
DATABASE_URL = (
    RAW_DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    if RAW_DATABASE_URL.startswith('postgres://')
    else RAW_DATABASE_URL
)
USE_POSTGRES = bool(DATABASE_URL and pgdb is not None)


def get_db_connection():
    """Create a database connection."""
    if USE_POSTGRES:
        parsed = urlparse(DATABASE_URL)
        return pgdb.connect(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
        )
    conn = sqlite3.connect(SQLITE_DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if USE_POSTGRES:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visitors (
                    id INTEGER PRIMARY KEY,
                    count INTEGER NOT NULL DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                INSERT INTO visitors (id, count, last_updated)
                VALUES (1, 0, CURRENT_TIMESTAMP)
                ON CONFLICT (id) DO NOTHING
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    count INTEGER NOT NULL DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('SELECT COUNT(*) FROM visitors')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO visitors (count) VALUES (0)')

        conn.commit()
        print('✅ Database initialized successfully!')
    finally:
        conn.close()


def add_contact(name, email, message):
    """Add a new contact message to the database."""
    query = '''
        INSERT INTO contacts (name, email, message)
        VALUES (%s, %s, %s)
    ''' if USE_POSTGRES else '''
        INSERT INTO contacts (name, email, message)
        VALUES (?, ?, ?)
    '''

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (name, email, message))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding contact: {e}")
        return False


def get_all_contacts():
    """Retrieve all contact messages."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts ORDER BY created_at DESC')
        contacts = cursor.fetchall()
        conn.close()
        return contacts
    except Exception as e:
        print(f"Error getting contacts: {e}")
        return []


def delete_contact(contact_id):
    """Delete a contact message by ID."""
    query = 'DELETE FROM contacts WHERE id = %s' if USE_POSTGRES else 'DELETE FROM contacts WHERE id = ?'

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (contact_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting contact: {e}")
        return False


def increment_visitor_count():
    """Increment and return the visitor count."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE visitors SET count = count + 1, last_updated = CURRENT_TIMESTAMP WHERE id = 1')
        cursor.execute('SELECT count FROM visitors WHERE id = 1')
        result = cursor.fetchone()
        count = result['count'] if result else 0
        conn.commit()
        conn.close()
        return count
    except Exception as e:
        print(f"Error incrementing visitor count: {e}")
        return 0


def get_visitor_count():
    """Get the current visitor count."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT count FROM visitors WHERE id = 1')
        result = cursor.fetchone()
        count = result['count'] if result else 0
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting visitor count: {e}")
        return 0


def reset_visitor_count():
    """Reset the visitor count to 0."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE visitors SET count = 0, last_updated = CURRENT_TIMESTAMP WHERE id = 1')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error resetting visitor count: {e}")
        return False


if __name__ == '__main__':
    init_database()
    print('Database setup complete!')
