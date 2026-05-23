import sqlite3
from app.config.settings import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")