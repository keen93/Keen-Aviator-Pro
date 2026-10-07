import sqlite3
from datetime import datetime

DATABASE = "aviator.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()

    connection.execute("""
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
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    connection.close()

    return [
        float(row["multiplier"])
        for row in reversed(rows)
    ]


def get_round_count():
    connection = get_connection()

    row = connection.execute(
        "SELECT COUNT(*) AS count FROM rounds"
    ).fetchone()

    connection.close()

    return row["count"]
