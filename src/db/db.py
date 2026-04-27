import sqlite3
import json 
from pathlib import Path

DB_PATH = "data/app.db"
VALID_STATUS = {"pending_review", "reviewed", "approved", "rejected"}

def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

    product_name TEXT,
    product_code TEXT,
    supplier TEXT,
    revision_date TEXT,
    version TEXT,
    language TEXT,
    annual_consumption_kg TEXT,
    storage_capacity_l TEXT,

    status TEXT DEFAULT 'pending_review',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
    """)

    cur.execute("PRAGMA table_info(extractions)")
    existing_columns = {row[1] for row in cur.fetchall()}

    metadata_columns = {
        "product_name": "TEXT",
        "product_code": "TEXT",
        "supplier": "TEXT",
        "revision_date": "TEXT",
        "version": "TEXT",
        "language": "TEXT",
        "annual_consumption_kg": "TEXT",
        "storage_capacity_l": "TEXT",
    }

    for column_name, column_type in metadata_columns.items():
        if column_name not in existing_columns:
            cur.execute(f"ALTER TABLE extractions ADD COLUMN {column_name} {column_type}")

    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_extractions_updated_at
    AFTER UPDATE ON extractions
    FOR EACH ROW
    BEGIN
        UPDATE extractions
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = OLD.id;
    END;
    """)
    conn.commit()
    conn.close()

def save_extraction(file_name, pdf_path, extracted_json):
    conn = get_connection()
    cur = conn.cursor()

    metadata = extracted_json.get("document_metadata", {}) or {}

    if metadata is None:
        metadata = {}

    operational_data = extracted_json.get("operational_data", {}) or {}

    cur.execute("""
    INSERT INTO extractions (
        file_name,
        pdf_path,
        extracted_json,
        product_name,
        product_code,
        supplier,
        revision_date,
        version,
        language,
        annual_consumption_kg,
        storage_capacity_l
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        file_name,
        pdf_path,
        json.dumps(extracted_json, ensure_ascii=False),
        metadata.get("product_name"),
        metadata.get("product_code"),
        metadata.get("supplier"),
        metadata.get("revision_date"),
        metadata.get("version"),
        metadata.get("language"),
        operational_data.get("annual_consumption_kg"),
        operational_data.get("storage_capacity_l")
    ))

    extraction_id = cur.lastrowid
    conn.commit()
    conn.close()
    return extraction_id

def get_all_extractions():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, file_name, status, created_at, updated_at, product_name, product_code, supplier, revision_date, version, language, annual_consumption_kg, storage_capacity_l
    FROM extractions
    ORDER BY created_at DESC
    """)
    rows = [dict(row) for row in cur.fetchall()]
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
    if row is None:
        return None
    result = dict(row)
    result["extracted_json"] = json.loads(result["extracted_json"])
    result["extracted_json"].setdefault("operational_data", {})
    result["extracted_json"]["operational_data"]["annual_consumption_kg"] = result.get("annual_consumption_kg")
    result["extracted_json"]["operational_data"]["storage_capacity_l"] = result.get("storage_capacity_l")
    return result


def update_extraction_json(extraction_id, new_json):
    conn = get_connection()
    cur = conn.cursor()

    metadata = new_json.get("document_metadata", {}) or {}
    operational_data = new_json.get("operational_data", {}) or {}

    cur.execute("""
    UPDATE extractions
    SET extracted_json = ?,
        product_name = ?,
        product_code = ?,
        supplier = ?,
        revision_date = ?,
        version = ?,
        language = ?,
        annual_consumption_kg = ?,
        storage_capacity_l = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (
        json.dumps(new_json, ensure_ascii=False),
        metadata.get("product_name"),
        metadata.get("product_code"),
        metadata.get("supplier"),
        metadata.get("revision_date"),
        metadata.get("version"),
        metadata.get("language"),
        operational_data.get("annual_consumption_kg"),
        operational_data.get("storage_capacity_l"),
        extraction_id,
    ))

    conn.commit()
    conn.close()

def update_operational_data(extraction_id, annual_consumption_kg=None, storage_capacity_l=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT extracted_json
    FROM extractions
    WHERE id = ?
    """, (extraction_id,))

    row = cur.fetchone()

    if row is None:
        conn.close()
        return

    extracted_json = json.loads(row["extracted_json"])
    extracted_json.setdefault("operational_data", {})

    extracted_json["operational_data"]["annual_consumption_kg"] = annual_consumption_kg
    extracted_json["operational_data"]["storage_capacity_l"] = storage_capacity_l

    cur.execute("""
    UPDATE extractions
    SET extracted_json = ?,
        annual_consumption_kg = ?,
        storage_capacity_l = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (
        json.dumps(extracted_json, ensure_ascii=False),
        annual_consumption_kg,
        storage_capacity_l,
        extraction_id,
    ))

    conn.commit()
    conn.close()

def update_extraction_status(extraction_id, status):
    if status not in VALID_STATUS:
        raise ValueError(f'Invalid status:{status}')
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE extractions
    SET status = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (status, extraction_id))

    conn.commit()
    conn.close()
