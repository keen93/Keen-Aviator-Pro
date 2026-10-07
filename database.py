import os
import sqlite3
from datetime import datetime
from urllib.parse import urlparse

DATABASE = "aviator.db"
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if DATABASE_URL:
        import pg8000.dbapi

        url = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )

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

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rounds (
                id SERIAL PRIMARY KEY,
                multiplier DOUBLE PRECISION NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.close()

    else:
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

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO rounds (multiplier, created_at)
            VALUES (%s, %s)
        """, (
            float(multiplier),
            datetime.now().isoformat(timespec="seconds")
        ))

        cursor.close()

    else:
        connection.execute("""
            INSERT INTO rounds (multiplier, created_at)
            VALUES (?, ?)
        """, (
            float(multiplier),
            datetime.now().isoformat(timespec="seconds")
        ))

    connection.commit()
    connection.close()


def get_recent_rounds(limit=200):
    connection = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT multiplier
            FROM rounds
            ORDER BY id DESC
            LIMIT %s
        """, (limit,))

        rows = cursor.fetchall()

        cursor.close()

        values = [
            float(row[0])
            for row in reversed(rows)
        ]

    else:
        rows = connection.execute("""
            SELECT multiplier
            FROM rounds
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        values = [
            float(row["multiplier"])
            for row in reversed(rows)
        ]

    connection.close()

    return values


def get_round_count():
    connection = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM rounds
        """)

        row = cursor.fetchone()

        cursor.close()

        count = row[0]

    else:
        row = connection.execute("""
            SELECT COUNT(*) AS count
            FROM rounds
        """).fetchone()

        count = row["count"]

    connection.close()

    return int(count)
