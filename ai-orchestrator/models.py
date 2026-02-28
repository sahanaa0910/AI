import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import Config

DB_PATH = Config.DATABASE_PATH


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'teacher',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                class_level TEXT NOT NULL,
                subject TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS grading_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                assignment_title TEXT NOT NULL,
                response_text TEXT NOT NULL,
                score REAL NOT NULL,
                feedback TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(teacher_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                class_level TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(teacher_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS iep_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                strengths TEXT NOT NULL,
                concerns TEXT NOT NULL,
                goals TEXT NOT NULL,
                accommodations TEXT NOT NULL,
                report_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(teacher_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'info',
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(teacher_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")
