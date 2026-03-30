"""
database.py - SQLite persistence layer

Handles:
- Database initialization
- Saving trip results
- Fetching recent trips
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "database/trips.db"


def get_connection():
    """Return a SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source      TEXT NOT NULL,
            destination TEXT NOT NULL,
            travel_date TEXT,
            preference  TEXT,
            best_mode   TEXT,
            best_co2    REAL,
            best_cost   REAL,
            co2_saved   REAL,
            result_json TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_trip(source: str, destination: str, travel_date: str,
              preference: str, result: dict):
    """Persist a planned trip to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    best = result.get("options", [{}])[0] if result.get("options") else {}
    summary = result.get("summary", {})

    cursor.execute("""
        INSERT INTO trips (source, destination, travel_date, preference,
                           best_mode, best_co2, best_cost, co2_saved, result_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source, destination, travel_date, preference,
        best.get("mode"),
        best.get("co2_kg"),
        best.get("cost_usd"),
        summary.get("co2_saved", 0),
        json.dumps(result),
    ))
    conn.commit()
    conn.close()


def get_recent_trips(limit: int = 5) -> list:
    """Fetch the most recent trip records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, source, destination, travel_date, preference,
               best_mode, best_co2, best_cost, co2_saved, created_at
        FROM trips
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
