"""MySQL access layer: connection pooling, schema setup and queries."""

from contextlib import contextmanager
from datetime import datetime

import mysql.connector
from mysql.connector import pooling

import config

COLUMNS = [
    "id", "person_name", "detected_at", "match_distance",
    "source", "source_name", "video_offset_sec",
]

_pool = None


def _connect_args(with_database=True):
    args = dict(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )
    if with_database:
        args["database"] = config.DB_NAME
    return args


def _get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="identitrack_pool",
            pool_size=config.DB_POOL_SIZE,
            **_connect_args(),
        )
    return _pool


@contextmanager
def get_connection():
    """Borrow a pooled connection; it is returned to the pool on exit."""
    conn = _get_pool().get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Create the database/table if missing and upgrade an old table in place."""
    conn = mysql.connector.connect(**_connect_args(with_database=False))
    try:
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}`")
        cur.execute(f"USE `{config.DB_NAME}`")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id               INT AUTO_INCREMENT PRIMARY KEY,
                person_name      VARCHAR(100) NOT NULL,
                detected_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                match_distance   FLOAT        NULL,
                source           VARCHAR(10)  NOT NULL DEFAULT 'live',
                source_name      VARCHAR(255) NULL,
                video_offset_sec FLOAT        NULL,
                INDEX idx_person_time (person_name, detected_at),
                INDEX idx_source (source, source_name)
            )
            """
        )
        # Upgrade path for tables created by the first version of the project.
        cur.execute(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'detections'",
            (config.DB_NAME,),
        )
        existing = {row[0] for row in cur.fetchall()}
        additions = {
            "match_distance": "FLOAT NULL",
            "source": "VARCHAR(10) NOT NULL DEFAULT 'live'",
            "source_name": "VARCHAR(255) NULL",
            "video_offset_sec": "FLOAT NULL",
        }
        for column, definition in additions.items():
            if column not in existing:
                cur.execute(f"ALTER TABLE detections ADD COLUMN {column} {definition}")
        conn.commit()
        cur.close()
    finally:
        conn.close()


def save_detection(person_name, event_time=None, distance=None,
                   source="live", source_name=None, video_offset_sec=None):
    """Log a single recognised person. Unknown faces are never stored."""
    if not person_name or person_name.startswith("Unknown"):
        return
    event_time = event_time or datetime.now()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO detections "
            "(person_name, detected_at, match_distance, source, source_name, video_offset_sec) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (person_name, event_time, distance, source, source_name, video_offset_sec),
        )
        conn.commit()
        cur.close()


def save_detections_bulk(rows):
    """Insert many rows in one round trip.

    Each row: (person_name, event_time, distance, source, source_name, video_offset_sec)
    """
    if not rows:
        return 0
    with get_connection() as conn:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO detections "
            "(person_name, detected_at, match_distance, source, source_name, video_offset_sec) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            rows,
        )
        conn.commit()
        count = cur.rowcount
        cur.close()
    return count


def fetch_detections():
    """Return every detection as a pandas DataFrame (newest first)."""
    import pandas as pd

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT {', '.join(COLUMNS)} FROM detections ORDER BY detected_at DESC"
        )
        rows = cur.fetchall()
        cur.close()
    return pd.DataFrame(rows, columns=COLUMNS)


def clear_detections(source=None):
    """Delete all records, or only those from one source ('live' / 'video')."""
    with get_connection() as conn:
        cur = conn.cursor()
        if source:
            cur.execute("DELETE FROM detections WHERE source = %s", (source,))
        else:
            cur.execute("DELETE FROM detections")
        conn.commit()
        deleted = cur.rowcount
        cur.close()
    return deleted


if __name__ == "__main__":
    print("Initialising database...")
    try:
        init_db()
        print("Database ready.")
    except Exception as exc:  # noqa: BLE001 - CLI convenience
        print(f"Failed: {exc}")
