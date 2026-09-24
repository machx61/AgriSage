"""SQLite storage for scan history and tracked plants."""

import base64
import datetime
import os
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

# AGRISAGE_DB lets a demo or test run use a separate database file
DATABASE_PATH = Path(os.environ.get("AGRISAGE_DB") or Path(__file__).resolve().parent.parent / "agrisage_history.db")
INDIA_TIMEZONE = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def now_ist() -> datetime.datetime:
    return datetime.datetime.now(INDIA_TIMEZONE)


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH, timeout=5)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaction():
    """Open a connection, commit on success (roll back on error), and always close it."""
    with closing(connect()) as conn, conn:
        yield conn


def _query(sql: str, params=()) -> list[tuple]:
    with closing(connect()) as conn:
        return conn.execute(sql, params).fetchall()


def _b64(photo: bytes | None) -> str:
    return base64.b64encode(photo).decode() if photo else ""


def _unb64(photo_b64: str | None) -> bytes | None:
    if not photo_b64:
        return None
    try:
        return base64.b64decode(photo_b64)
    except ValueError:
        return None


def init_db():
    """Create tables if they don't exist and apply small migrations."""
    with transaction() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scans
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      session_id TEXT,
                      date TEXT,
                      disease TEXT,
                      confidence REAL,
                      raw_class TEXT)''')
        existing_columns = {row[1] for row in c.execute("PRAGMA table_info(scans)")}
        if "session_id" not in existing_columns:
            c.execute("ALTER TABLE scans ADD COLUMN session_id TEXT")
        if "raw_class" not in existing_columns:
            c.execute("ALTER TABLE scans ADD COLUMN raw_class TEXT")
        c.execute("CREATE INDEX IF NOT EXISTS idx_scans_session_id ON scans(session_id)")

        c.execute('''CREATE TABLE IF NOT EXISTS tracked_plants
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      device_id TEXT,
                      plant_name TEXT,
                      crop_type TEXT,
                      initial_disease TEXT,
                      created_date TEXT,
                      current_status TEXT DEFAULT 'stable',
                      current_score INTEGER DEFAULT 50,
                      next_checkin_date TEXT)''')
        c.execute("CREATE INDEX IF NOT EXISTS idx_tracked_device ON tracked_plants(device_id)")

        c.execute('''CREATE TABLE IF NOT EXISTS progress_entries
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      plant_id INTEGER,
                      date TEXT,
                      disease_detected TEXT,
                      confidence REAL,
                      health_score INTEGER,
                      status_label TEXT,
                      ai_notes TEXT,
                      adjusted_treatment TEXT,
                      next_checkin_days INTEGER,
                      photo_b64 TEXT,
                      FOREIGN KEY (plant_id) REFERENCES tracked_plants(id))''')
        c.execute("CREATE INDEX IF NOT EXISTS idx_progress_plant ON progress_entries(plant_id)")


# --- Scan history ---

def save_scan(session_id: str, raw_class: str, disease_name: str, confidence: float):
    with transaction() as conn:
        conn.execute(
            "INSERT INTO scans (session_id, date, disease, confidence, raw_class) VALUES (?, ?, ?, ?, ?)",
            (session_id, now_ist().strftime("%Y-%m-%d %H:%M"), disease_name, confidence, raw_class),
        )


def get_past_scans(session_id: str, limit: int = 10) -> list[tuple]:
    """Return (date, disease, confidence, raw_class) rows, newest first."""
    return _query(
        "SELECT date, disease, confidence, raw_class FROM scans WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit),
    )


# --- Plant tracking ---

def get_tracked_plants(device_id: str) -> list[tuple]:
    """Return (id, plant_name, crop_type, initial_disease, created_date,
    current_status, current_score, next_checkin_date) rows, newest first."""
    return _query(
        '''SELECT id, plant_name, crop_type, initial_disease, created_date, current_status, current_score, next_checkin_date
           FROM tracked_plants WHERE device_id = ? ORDER BY id DESC''',
        (device_id,),
    )


_ENTRY_KEYS = ["date", "disease", "confidence", "health_score", "status_label", "ai_notes",
               "adjusted_treatment", "next_checkin_days", "photo"]


def get_progress_entries(plant_id: int) -> list[dict]:
    """Return a plant's check-ins, oldest first, with photos as JPEG bytes."""
    rows = _query(
        '''SELECT date, disease_detected, confidence, health_score, status_label, ai_notes,
                  adjusted_treatment, next_checkin_days, photo_b64
           FROM progress_entries WHERE plant_id = ? ORDER BY id ASC''',
        (plant_id,),
    )
    entries = [dict(zip(_ENTRY_KEYS, row)) for row in rows]
    for entry in entries:
        entry["photo"] = _unb64(entry["photo"])
    return entries


def get_latest_entry(plant_id: int) -> dict | None:
    entries = get_progress_entries(plant_id)
    return entries[-1] if entries else None


def _next_checkin(days: int) -> str:
    return (now_ist() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")


def _insert_entry(conn, plant_id, now_str, disease_name, confidence, result, treatment, photo):
    conn.execute(
        '''INSERT INTO progress_entries (plant_id, date, disease_detected, confidence, health_score, status_label,
                                         ai_notes, adjusted_treatment, next_checkin_days, photo_b64)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (plant_id, now_str, disease_name, confidence, result["health_score"], result["status_label"],
         result["ai_notes"], treatment, result["next_checkin_days"], _b64(photo)),
    )


def add_plant(device_id: str, plant_name: str, raw_class: str, disease_name: str,
              confidence: float, assessment: dict, photo: bytes | None) -> str:
    """Create a tracked plant with its first check-in. Returns the next check-in date."""
    crop_type = raw_class.split("_")[0]
    now_str = now_ist().strftime("%Y-%m-%d %H:%M")
    next_date = _next_checkin(assessment["next_checkin_days"])
    with transaction() as conn:
        cursor = conn.execute(
            '''INSERT INTO tracked_plants (device_id, plant_name, crop_type, initial_disease, created_date,
                                           current_status, current_score, next_checkin_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (device_id, plant_name, crop_type, raw_class, now_str,
             assessment["status_label"], assessment["health_score"], next_date),
        )
        _insert_entry(conn, cursor.lastrowid, now_str, disease_name, confidence, assessment, "", photo)
    return next_date


def add_checkin(plant_id: int, disease_name: str, confidence: float, result: dict, photo: bytes | None) -> str:
    """Record a progress check-in and update the plant. Returns the next check-in date."""
    now_str = now_ist().strftime("%Y-%m-%d %H:%M")
    next_date = _next_checkin(result["next_checkin_days"])
    with transaction() as conn:
        _insert_entry(conn, plant_id, now_str, disease_name, confidence, result,
                      result.get("treatment_adjustments", ""), photo)
        conn.execute(
            "UPDATE tracked_plants SET current_status = ?, current_score = ?, next_checkin_date = ? WHERE id = ?",
            (result["status_label"], result["health_score"], next_date, plant_id),
        )
    return next_date


def delete_plant(plant_id: int):
    with transaction() as conn:
        conn.execute("DELETE FROM progress_entries WHERE plant_id = ?", (plant_id,))
        conn.execute("DELETE FROM tracked_plants WHERE id = ?", (plant_id,))
