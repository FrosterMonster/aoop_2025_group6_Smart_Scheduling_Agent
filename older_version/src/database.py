import sqlite3
import os

DB_PATH = "user_data.db"

def init_db():
    """Initialize the database with a preferences table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def set_preference(key: str, value: str):
    """Save or update a user preference."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_preference(key: str):
    """Retrieve a single preference by key."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value FROM preferences WHERE key = ?', (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_preferences():
    """Retrieve all preferences as a dictionary."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT key, value FROM preferences')
    results = c.fetchall()
    conn.close()
    return {k: v for k, v in results}

# Initialize the database immediately when this module is imported
init_db()