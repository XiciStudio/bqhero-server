"""Database connection management (SQLite)."""

import os
import sqlite3
import threading

import config

_conn_local = threading.local()


def get_db() -> sqlite3.Connection:
    """Get thread-local database connection."""
    conn = getattr(_conn_local, "conn", None)
    if conn is None:
        db_dir = os.path.dirname(config.DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        _conn_local.conn = conn
    return conn


def init_db():
    """Initialize database connection (lazy — won't connect until first use)."""
    _conn_local.conn = None


def query_one(sql: str, params: tuple = None):
    """Execute query and return single row (as dict-like Row)."""
    conn = get_db()
    cur = conn.execute(sql, params or ())
    return cur.fetchone()


def query_all(sql: str, params: tuple = None):
    """Execute query and return all rows."""
    conn = get_db()
    cur = conn.execute(sql, params or ())
    return cur.fetchall()


def execute(sql: str, params: tuple = None):
    """Execute update/insert/delete. Auto-commits."""
    conn = get_db()
    conn.execute(sql, params or ())
    conn.commit()
