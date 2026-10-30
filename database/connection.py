"""
Database connection manager for SQLite.
Configured with WAL mode and foreign key constraints enabled.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
from config.settings import DB_PATH, get_logger

logger = get_logger(__name__)

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create a configured SQLite connection."""
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

@contextmanager
def get_db_cursor(db_path: Path = DB_PATH) -> Generator[sqlite3.Cursor, None, None]:
    """Context manager yielding a cursor inside an automatic transaction."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
