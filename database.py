import os
import sqlite3
from datetime import datetime

DATABASE = "aviator.db"
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if DATABASE_URL:
        import pg8000.dbapi

        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)

        from urllib.parse import urlparse

        parsed = urlparse(url)

        return pg8000.dbapi.connect(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip("/")
        )

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS rounds (
            id SERIAL PRIMARY KEY,
            multiplier DOUBLE PRECISION NOT NULL,
            created_at TEXT NOT NULL
        )
    """ if DATABASE_URL else """
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            multiplier REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def add_round(multiplier):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO rounds (multiplier, created_at)
        VALUES (%s, %s)
        """ if DATABASE_URL else """
        INSERT INTO rounds (multiplier, created_at)
        VALUES (?, ?)
        """,
        (
            float(multiplier),
            datetime.now().isoformat(timespec="seconds")
        )
    )

    connection.commit()
    connection.close()


def get_recent_rounds(limit=200):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT multiplier
        FROM rounds
        ORDER BY id DESC
        LIMIT %s
        """ if DATABASE_URL else """
        SELECT multiplier
        FROM rounds
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    connection.close()

    return [
        float(row[0] if DATABASE_URL else row["multiplier"])
        for row in reversed(rows)
    ]


def get_round_count():
    connection = get_connection()

    row = connection.execute(
        "SELECT COUNT(*) AS count FROM rounds"
    ).fetchone()

    connection.close()

    return int(row[0] if DATABASE_URL else row["count"])
