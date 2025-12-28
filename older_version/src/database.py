import sqlite3
import os

DB_PATH = "user_data.db"

def init_db():
    """Initialize the database with a preferences table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def set_preference(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_preference(key: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value FROM preferences WHERE key = ?', (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_preferences():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT key, value FROM preferences')
    results = c.fetchall()
    conn.close()
    return {k: v for k, v in results}

# Initialize when imported
init_db()