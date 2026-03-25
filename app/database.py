"""SQLite database connection helpers and schema initialization."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

DATABASE_PATH: str = os.environ.get("DATABASE_PATH", "cleargrade.db")

_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name TEXT NOT NULL,
    website_url TEXT NOT NULL,
    industry TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    email TEXT NOT NULL,
    slug TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    approved_at DATETIME,
    sent_at DATETIME,
    error_log TEXT,
    dashboard_url TEXT
);
"""


def _connect() -> sqlite3.Connection:
    """Create a new SQLite connection with row-factory set to dict."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a database connection, committing on success and rolling back on error."""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the jobs table if it does not already exist."""
    with get_db() as conn:
        conn.executescript(_SCHEMA_SQL)
