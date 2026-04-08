"""
CDGI Faculty Attendance System — Database
"""

import sqlite3, os, json
from datetime import datetime

DB_NAME              = "attendance.db"
REGISTERED_FACES_DIR = os.path.join("static", "faces", "registered")
ATTENDANCE_FACES_DIR = os.path.join("static", "faces", "attendance")


def ensure_dirs():
    os.makedirs(REGISTERED_FACES_DIR, exist_ok=True)
    os.makedirs(ATTENDANCE_FACES_DIR, exist_ok=True)
    os.makedirs(os.path.join("static", "images"), exist_ok=True)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    ensure_dirs()
    conn = get_db()

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS faculty (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id         TEXT    UNIQUE NOT NULL COLLATE NOCASE,
        name                TEXT    NOT NULL,
        email               TEXT    UNIQUE NOT NULL COLLATE NOCASE,
        phone               TEXT,
        department          TEXT    NOT NULL,
        designation         TEXT    NOT NULL,
        password_hash       TEXT    NOT NULL,
        face_descriptor     TEXT,
        face_image_path     TEXT,
        has_face_registered INTEGER NOT NULL DEFAULT 0,
        role                TEXT    NOT NULL DEFAULT 'faculty',
        is_active           INTEGER NOT NULL DEFAULT 1,
        notes               TEXT,
        created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id            INTEGER NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
        employee_id           TEXT    NOT NULL REFERENCES faculty(employee_id) ON DELETE CASCADE,
        attendance_date       DATE    NOT NULL,
        check_in_time         TEXT,
        check_out_time        TEXT,
        check_in_image_path   TEXT,
        check_out_image_path  TEXT,
        check_in_lat          REAL,
        check_in_lng          REAL,
        check_out_lat         REAL,
        check_out_lng         REAL,
        working_hours         REAL    DEFAULT 0,
        status                TEXT    DEFAULT 'present',
        marked_by_admin       INTEGER DEFAULT 0,
        notes                 TEXT,
        created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(faculty_id, attendance_date)
    );

    CREATE TABLE IF NOT EXISTS leave_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id  INTEGER NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
        employee_id TEXT    NOT NULL,
        leave_date  DATE    NOT NULL,
        leave_type  TEXT    DEFAULT 'absent',
        reason      TEXT,
        marked_by   INTEGER,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(faculty_id, leave_date)
    );

    CREATE TABLE IF NOT EXISTS admin_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id    INTEGER NOT NULL REFERENCES faculty(id),
        action      TEXT    NOT NULL,
        target_id   INTEGER,
        details     TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    existing = conn.execute(
        "SELECT id FROM faculty WHERE employee_id='ADMIN001'"
    ).fetchone()

    if not existing:
        import bcrypt
        pw_hash = bcrypt.hashpw(b"admin@CDGI2025", bcrypt.gensalt()).decode()
        conn.execute("""
            INSERT INTO faculty
              (employee_id, name, email, phone, department, designation,
               password_hash, has_face_registered, role)
            VALUES
              ('ADMIN001','System Administrator','admin@cdgi.edu.in','0731-2970011',
               'Administration','System Admin', ?, 0, 'admin')
        """, [pw_hash])
        conn.commit()
        print("[DB] Admin account created → ID: ADMIN001 | Password: admin@CDGI2025")

    conn.commit()
    conn.close()
    print("[DB] Database initialised successfully.")
