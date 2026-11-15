from __future__ import annotations

import os
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "circe.db"
DB_PATH = Path(os.getenv("CIRCE_DB_PATH", str(DEFAULT_DB_PATH)))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS progress (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    level_id TEXT NOT NULL,
    active_node TEXT NOT NULL,
    scenario_completed INTEGER NOT NULL DEFAULT 0,
    score REAL NOT NULL DEFAULT 0,
    xp INTEGER NOT NULL DEFAULT 0,
    lives INTEGER NOT NULL DEFAULT 3,
    max_lives INTEGER NOT NULL DEFAULT 3,
    attempts INTEGER NOT NULL DEFAULT 0,
    containment INTEGER NOT NULL DEFAULT 35,
    data_safety INTEGER NOT NULL DEFAULT 50,
    service_health INTEGER NOT NULL DEFAULT 60,
    node_results TEXT NOT NULL DEFAULT '{}',
    updated_at REAL NOT NULL,
    PRIMARY KEY (user_id, level_id)
);
"""


def get_connection() -> sqlite3.Connection:
    """Abre (y si hace falta crea) la base de datos local SQLite de CIRCE."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(_SCHEMA)
    return connection
