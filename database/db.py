import sqlite3
import os
from config import Config

def get_db_connection():
    """Returns a connection to the SQLite database with row_factory enabled."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH) or ".", exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        original_image_path TEXT NOT NULL,
        annotated_image_path TEXT NOT NULL,
        total_onions INTEGER NOT NULL,
        good_count INTEGER NOT NULL DEFAULT 0,
        damaged_count INTEGER NOT NULL DEFAULT 0,
        rotten_count INTEGER NOT NULL DEFAULT 0,
        sprouted_count INTEGER NOT NULL DEFAULT 0,
        undersized_count INTEGER NOT NULL DEFAULT 0,
        good_percentage REAL NOT NULL DEFAULT 0.0,
        damaged_percentage REAL NOT NULL DEFAULT 0.0,
        rotten_percentage REAL NOT NULL DEFAULT 0.0,
        sprouted_percentage REAL NOT NULL DEFAULT 0.0,
        undersized_percentage REAL NOT NULL DEFAULT 0.0,
        quality_score REAL NOT NULL DEFAULT 0.0,
        preliminary_grade TEXT NOT NULL,
        average_confidence REAL NOT NULL DEFAULT 0.0,
        ai_mode TEXT NOT NULL DEFAULT 'demo',
        pdf_path TEXT,
        detections_json TEXT
    );
    """)
    
    conn.commit()
    conn.close()
