"""
Database Module for Portfolio Website
Handles SQLite operations for contacts and visitor tracking
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(BASE_DIR, 'portfolio.db')

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create visitors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count INTEGER NOT NULL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize visitor count if not exists
    cursor.execute('SELECT COUNT(*) FROM visitors')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO visitors (count) VALUES (0)')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def add_contact(name, email, message):
    """Add a new contact message to the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contacts (name, email, message)
            VALUES (?, ?, ?)
        ''', (name, email, message))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding contact: {e}")
        return False

def get_all_contacts():
    """Retrieve all contact messages"""
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
    """Delete a contact message by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting contact: {e}")
        return False

def increment_visitor_count():
    """Increment and return the visitor count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Increment visitor count
        cursor.execute('UPDATE visitors SET count = count + 1, last_updated = CURRENT_TIMESTAMP WHERE id = 1')
        
        # Get updated count
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
    """Get the current visitor count"""
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
    """Reset the visitor count to 0"""
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
    print("Database setup complete!")
