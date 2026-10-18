"""Storage for accounts, scan history and tracked plants.

Uses Postgres when DATABASE_URL is set (environment variable or Streamlit
secret) and a local SQLite file otherwise. SQL is written once with `?`
placeholders and translated for Postgres.
"""

import base64
import datetime
import os
import sqlite3
import time
from contextlib import closing, contextmanager
from pathlib import Path

# AGRISAGE_DB lets a demo or test run use a separate database file
DATABASE_PATH = Path(os.environ.get("AGRISAGE_DB") or Path(__file__).resolve().parent.parent / "agrisage_history.db")
INDIA_TIMEZONE = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

_initialized: set[str] = set()


def now_ist() -> datetime.datetime:
    return datetime.datetime.now(INDIA_TIMEZONE)


def _database_url() -> str | None:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    try:
        import streamlit as st
        return st.secrets.get("DATABASE_URL") or None
    except Exception:  # no secrets file, or running outside Streamlit
        return None


_pools: dict = {}


def _pool(url: str):
    """One small pool of open connections per database, shared by all sessions.

    Opening a fresh connection to a hosted database costs about a second, so
    connections are kept alive and checked before reuse (the host may have
    closed an idle one).
    """
    if url not in _pools:
        from psycopg_pool import ConnectionPool
        # prepare_threshold=None: connection poolers (Supabase, Neon) reject prepared statements
        _pools[url] = ConnectionPool(
            url, min_size=1, max_size=5, timeout=15, open=True, check=ConnectionPool.check_connection,
            kwargs={"connect_timeout": 10, "prepare_threshold": None},
        )
    return _pools[url]


class _PgConnection:
    """A pooled psycopg connection that accepts `?` placeholders like sqlite3 does.

    As a context manager it commits on success and rolls back on error;
    `close()` hands the connection back to the pool.
    """

    def __init__(self, pool):
        self._pool = pool
        self._conn = pool.getconn()

    def execute(self, sql: str, params=()):
        return self._conn.execute(sql.replace("%", "%%").replace("?", "%s"), params)  # literal % must be escaped

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()

    def close(self):
        self._pool.putconn(self._conn)


def _is_postgres(conn) -> bool:
    return isinstance(conn, _PgConnection)


def connect():
    url = _database_url()
    if url:
        return _PgConnection(_pool(url))
    conn = sqlite3.connect(DATABASE_PATH, timeout=5)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaction():
    """Open a connection, commit on success (roll back on error), and always close it."""
    with closing(connect()) as conn, conn:
        yield conn


def _query(sql: str, params=()) -> list[tuple]:
    with transaction() as conn:  # ends the transaction so a pooled connection goes back clean
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


def _columns(conn, table: str) -> set[str]:
    if _is_postgres(conn):
        rows = conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = ? AND table_schema = current_schema()",
            (table,),
        ).fetchall()
        return {row[0] for row in rows}
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def init_db():
    """Create tables if they don't exist and apply small migrations (once per process and database)."""
    target = _database_url() or str(DATABASE_PATH)
    if target in _initialized:
        return
    with transaction() as conn:
        if _is_postgres(conn):
            conn.execute("SELECT pg_advisory_xact_lock(727274)")  # concurrent first runs
            pk = "SERIAL PRIMARY KEY"
        else:
            pk = "INTEGER PRIMARY KEY AUTOINCREMENT"

        conn.execute(f'''CREATE TABLE IF NOT EXISTS users
                         (id {pk},
                          username TEXT NOT NULL UNIQUE,
                          password_hash TEXT NOT NULL,
                          created_at BIGINT NOT NULL,
                          failed_attempts INTEGER NOT NULL DEFAULT 0,
                          locked_until BIGINT NOT NULL DEFAULT 0)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS auth_sessions
                        (token_hash TEXT PRIMARY KEY,
                         user_id INTEGER NOT NULL REFERENCES users(id),
                         expires_at BIGINT NOT NULL)''')

        conn.execute(f'''CREATE TABLE IF NOT EXISTS scans
                         (id {pk},
                          session_id TEXT,
                          date TEXT,
                          disease TEXT,
                          confidence DOUBLE PRECISION,
                          raw_class TEXT)''')
        existing = _columns(conn, "scans")
        if "session_id" not in existing:
            conn.execute("ALTER TABLE scans ADD COLUMN session_id TEXT")
        if "raw_class" not in existing:
            conn.execute("ALTER TABLE scans ADD COLUMN raw_class TEXT")
        if "user_id" not in existing:
            conn.execute("ALTER TABLE scans ADD COLUMN user_id INTEGER")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_session_id ON scans(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id)")

        conn.execute(f'''CREATE TABLE IF NOT EXISTS tracked_plants
                         (id {pk},
                          device_id TEXT,
                          plant_name TEXT,
                          crop_type TEXT,
                          initial_disease TEXT,
                          created_date TEXT,
                          current_status TEXT DEFAULT 'stable',
                          current_score INTEGER DEFAULT 50,
                          next_checkin_date TEXT)''')
        if "user_id" not in _columns(conn, "tracked_plants"):
            conn.execute("ALTER TABLE tracked_plants ADD COLUMN user_id INTEGER")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tracked_device ON tracked_plants(device_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tracked_user ON tracked_plants(user_id)")

        conn.execute(f'''CREATE TABLE IF NOT EXISTS progress_entries
                         (id {pk},
                          plant_id INTEGER,
                          date TEXT,
                          disease_detected TEXT,
                          confidence DOUBLE PRECISION,
                          health_score INTEGER,
                          status_label TEXT,
                          ai_notes TEXT,
                          adjusted_treatment TEXT,
                          next_checkin_days INTEGER,
                          photo_b64 TEXT,
                          FOREIGN KEY (plant_id) REFERENCES tracked_plants(id))''')
        conn.execute("CREATE INDEX IF NOT EXISTS idx_progress_plant ON progress_entries(plant_id)")
    _initialized.add(target)


# --- Accounts ---

_USER_KEYS = ["id", "username", "password_hash", "failed_attempts", "locked_until"]
_USER_COLUMNS = ", ".join(_USER_KEYS)


def create_user(username: str, password_hash: str) -> int | None:
    """Insert a user. Returns the new id, or None if the username is taken."""
    with transaction() as conn:
        row = conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?) "
            "ON CONFLICT (username) DO NOTHING RETURNING id",
            (username, password_hash, int(time.time())),
        ).fetchone()
    return row[0] if row else None


def get_user_by_username(username: str) -> dict | None:
    rows = _query(f"SELECT {_USER_COLUMNS} FROM users WHERE username = ?", (username,))
    return dict(zip(_USER_KEYS, rows[0])) if rows else None


def record_failed_login(user_id: int, max_attempts: int, lock_seconds: int):
    """Count a failed login; after `max_attempts` lock the account and reset the counter."""
    with transaction() as conn:
        (failed,) = conn.execute("SELECT failed_attempts FROM users WHERE id = ?", (user_id,)).fetchone()
        failed += 1
        if failed >= max_attempts:
            conn.execute("UPDATE users SET failed_attempts = 0, locked_until = ? WHERE id = ?",
                         (int(time.time()) + lock_seconds, user_id))
        else:
            conn.execute("UPDATE users SET failed_attempts = ? WHERE id = ?", (failed, user_id))


def reset_failed_logins(user_id: int):
    with transaction() as conn:
        conn.execute("UPDATE users SET failed_attempts = 0, locked_until = 0 WHERE id = ?", (user_id,))


def create_auth_session(token_hash: str, user_id: int, expires_at: int):
    with transaction() as conn:
        conn.execute("DELETE FROM auth_sessions WHERE expires_at < ?", (int(time.time()),))
        conn.execute("INSERT INTO auth_sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
                     (token_hash, user_id, expires_at))


def get_session_user(token_hash: str) -> dict | None:
    """Return {"id", "username"} for a live session token hash, else None."""
    rows = _query(
        '''SELECT u.id, u.username FROM auth_sessions s JOIN users u ON u.id = s.user_id
           WHERE s.token_hash = ? AND s.expires_at > ?''',
        (token_hash, int(time.time())),
    )
    return {"id": rows[0][0], "username": rows[0][1]} if rows else None


def delete_auth_session(token_hash: str):
    with transaction() as conn:
        conn.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (token_hash,))


def claim_device_data(user_id: int, device_id: str):
    """Attach rows saved under a browser's old device ID to an account (only rows no account owns yet)."""
    with transaction() as conn:
        conn.execute("UPDATE scans SET user_id = ? WHERE session_id = ? AND user_id IS NULL", (user_id, device_id))
        conn.execute("UPDATE tracked_plants SET user_id = ? WHERE device_id = ? AND user_id IS NULL",
                     (user_id, device_id))


# --- Scan history ---

def save_scan(user_id: int, raw_class: str, disease_name: str, confidence: float):
    with transaction() as conn:
        conn.execute(
            "INSERT INTO scans (user_id, date, disease, confidence, raw_class) VALUES (?, ?, ?, ?, ?)",
            (user_id, now_ist().strftime("%Y-%m-%d %H:%M"), disease_name, confidence, raw_class),
        )


def get_past_scans(user_id: int, limit: int = 10) -> list[tuple]:
    """Return (date, disease, confidence, raw_class) rows, newest first."""
    return _query(
        "SELECT date, disease, confidence, raw_class FROM scans WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )


# --- Plant tracking ---

def get_tracked_plants(user_id: int) -> list[tuple]:
    """Return (id, plant_name, crop_type, initial_disease, created_date,
    current_status, current_score, next_checkin_date) rows, newest first."""
    return _query(
        '''SELECT id, plant_name, crop_type, initial_disease, created_date, current_status, current_score, next_checkin_date
           FROM tracked_plants WHERE user_id = ? ORDER BY id DESC''',
        (user_id,),
    )


_ENTRY_KEYS = ["date", "disease", "confidence", "health_score", "status_label", "ai_notes",
               "adjusted_treatment", "next_checkin_days", "photo"]


def get_progress_entries(plant_id: int, user_id: int) -> list[dict]:
    """Return a plant's check-ins, oldest first, with photos as JPEG bytes. Empty if the plant isn't the user's."""
    rows = _query(
        '''SELECT e.date, e.disease_detected, e.confidence, e.health_score, e.status_label, e.ai_notes,
                  e.adjusted_treatment, e.next_checkin_days, e.photo_b64
           FROM progress_entries e JOIN tracked_plants p ON p.id = e.plant_id
           WHERE e.plant_id = ? AND p.user_id = ? ORDER BY e.id ASC''',
        (plant_id, user_id),
    )
    entries = [dict(zip(_ENTRY_KEYS, row)) for row in rows]
    for entry in entries:
        entry["photo"] = _unb64(entry["photo"])
    return entries


def get_latest_entry(plant_id: int, user_id: int) -> dict | None:
    entries = get_progress_entries(plant_id, user_id)
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


def add_plant(user_id: int, plant_name: str, raw_class: str, disease_name: str,
              confidence: float, assessment: dict, photo: bytes | None) -> str:
    """Create a tracked plant with its first check-in. Returns the next check-in date."""
    crop_type = raw_class.split("_")[0]
    now_str = now_ist().strftime("%Y-%m-%d %H:%M")
    next_date = _next_checkin(assessment["next_checkin_days"])
    with transaction() as conn:
        (plant_id,) = conn.execute(
            '''INSERT INTO tracked_plants (user_id, plant_name, crop_type, initial_disease, created_date,
                                           current_status, current_score, next_checkin_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id''',
            (user_id, plant_name, crop_type, raw_class, now_str,
             assessment["status_label"], assessment["health_score"], next_date),
        ).fetchone()
        _insert_entry(conn, plant_id, now_str, disease_name, confidence, assessment, "", photo)
    return next_date


def add_checkin(plant_id: int, user_id: int, disease_name: str, confidence: float,
                result: dict, photo: bytes | None) -> str:
    """Record a progress check-in and update the plant. Returns the next check-in date.

    Raises PermissionError if the plant doesn't belong to the user.
    """
    now_str = now_ist().strftime("%Y-%m-%d %H:%M")
    next_date = _next_checkin(result["next_checkin_days"])
    with transaction() as conn:
        updated = conn.execute(
            "UPDATE tracked_plants SET current_status = ?, current_score = ?, next_checkin_date = ? "
            "WHERE id = ? AND user_id = ? RETURNING id",
            (result["status_label"], result["health_score"], next_date, plant_id, user_id),
        ).fetchone()
        if updated is None:
            raise PermissionError("Plant not found for this user")
        _insert_entry(conn, plant_id, now_str, disease_name, confidence, result,
                      result.get("treatment_adjustments", ""), photo)
    return next_date


def delete_plant(plant_id: int, user_id: int):
    """Delete a plant and its check-ins. Does nothing if the plant isn't the user's."""
    with transaction() as conn:
        conn.execute(
            "DELETE FROM progress_entries WHERE plant_id IN (SELECT id FROM tracked_plants WHERE id = ? AND user_id = ?)",
            (plant_id, user_id),
        )
        conn.execute("DELETE FROM tracked_plants WHERE id = ? AND user_id = ?", (plant_id, user_id))
