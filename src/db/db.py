import sqlite3
import json 

DB_PATH = "data/app.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""

    CREATE TABLE IF NOT EXISTS extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                pdf_path TEXT NOT NULL,
                extracted_json TEXT NOT NULL,
                status TEXT DEFAULT 'pending_review',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
    """)
    conn.commit()
    conn.close()

def save_extraction(file_name, pdf_path, extracted_json):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO extractions (file_name, pdf_path, extracted_json)
                VALUES(?,?,?)
                """, (file_name, pdf_path, json.dumps(extracted_json)))
    conn.commit()
    conn.close()

def get_all_extractions():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, file_name, status, created_at FROM extractions
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_extraction_by_id(extraction_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" 
    SELECT * FROM extractions WHERE id = ?
    """, (extraction_id,))

    row = cur.fetchone()
    conn.close()
    return row


def update_extraction_json(extraction_id, new_json):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE extractions
    SET extracted_json = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ? 
    """, (json.dumps(new_json), extraction_id))

    conn.commit()
    conn.close()

def update_extraction_status(extraction_id, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE extractions
    SET status = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (status, extraction_id))

    conn.commit()
    conn.close()

