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


def init_performance_table():
    connection = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id SERIAL PRIMARY KEY,
                signal TEXT NOT NULL,
                confidence DOUBLE PRECISION NOT NULL,
                level TEXT NOT NULL,
                average DOUBLE PRECISION,
                volatility DOUBLE PRECISION,
                rounds INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                outcome TEXT DEFAULT 'PENDING',
                outcome_multiplier DOUBLE PRECISION
            )
        """)

        cursor.close()

    else:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal TEXT NOT NULL,
                confidence REAL NOT NULL,
                level TEXT NOT NULL,
                average REAL,
                volatility REAL,
                rounds INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                outcome TEXT DEFAULT 'PENDING',
                outcome_multiplier REAL
            )
        """)

    connection.commit()
    connection.close()


def save_signal(result):
    connection = get_connection()

    values = (
        result.get("signal", "WAIT"),
        float(result.get("confidence", 0)),
        result.get("level", "UNKNOWN"),
        result.get("average"),
        result.get("volatility"),
        int(result.get("rounds", 0)),
        datetime.now().isoformat(timespec="seconds")
    )

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO signals (
                signal,
                confidence,
                level,
                average,
                volatility,
                rounds,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, values)

        cursor.close()

    else:
        connection.execute("""
            INSERT INTO signals (
                signal,
                confidence,
                level,
                average,
                volatility,
                rounds,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, values)

    connection.commit()
    connection.close()


def record_outcome(signal_id, outcome, multiplier):
    outcome = str(outcome).upper().strip()
    multiplier = float(multiplier)

    if outcome not in ("WIN", "LOSS"):
        raise ValueError("Outcome must be WIN or LOSS")

    if multiplier <= 0:
        raise ValueError("Multiplier must be greater than 0")

    connection = get_connection()

    values = (
        outcome,
        multiplier,
        int(signal_id)
    )

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE signals
            SET outcome = %s,
                outcome_multiplier = %s
            WHERE id = %s
            AND outcome = 'PENDING'
        """, values)

        updated = cursor.rowcount

        cursor.close()

    else:
        cursor = connection.execute("""
            UPDATE signals
            SET outcome = ?,
                outcome_multiplier = ?
            WHERE id = ?
            AND outcome = 'PENDING'
        """, values)

        updated = cursor.rowcount

    connection.commit()
    connection.close()

    return updated


def get_signal_count():
    connection = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM signals
        """)

        row = cursor.fetchone()

        cursor.close()

        count = row[0]

    else:
        row = connection.execute("""
            SELECT COUNT(*) AS count
            FROM signals
        """).fetchone()

        count = row["count"]

    connection.close()

    return int(count)


def get_signal_history(limit=50):
    connection = get_connection()

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                signal,
                confidence,
                level,
                average,
                volatility,
                rounds,
                created_at,
                outcome,
                outcome_multiplier
            FROM signals
            ORDER BY id DESC
            LIMIT %s
        """, (limit,))

        rows = cursor.fetchall()

        cursor.close()

        columns = [
            "id",
            "signal",
            "confidence",
            "level",
            "average",
            "volatility",
            "rounds",
            "created_at",
            "outcome",
            "outcome_multiplier"
        ]

        result = [
            dict(zip(columns, row))
            for row in rows
        ]

    else:
        rows = connection.execute("""
            SELECT
                id,
                signal,
                confidence,
                level,
                average,
                volatility,
                rounds,
                created_at,
                outcome,
                outcome_multiplier
            FROM signals
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        result = [
            dict(row)
            for row in rows
        ]

    connection.close()

    return result
