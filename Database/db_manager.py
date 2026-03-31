"""
Database Manager – central point for all local SQLite operations.
Handles connection, table creation, CRUD with automatic sync-log tracking.
"""

import sqlite3
import json
import os
import threading
from Database.models import TABLES_SQL, new_uuid, utc_now
from Database.sync_log import SYNC_LOG_TABLE_SQL, add_sync_log, SyncAction

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "accounting.db")


class DatabaseManager:
    """Singleton-style wrapper around the local SQLite database."""

    _instance = None
    _tls = threading.local()   # per-thread connection storage

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        os.makedirs(DB_DIR, exist_ok=True)
        self.db_path = DB_PATH
        self._initialized = True

    # ── Connection ───────────────────────────────────────────────────────────

    def connect(self):
        """Open (or reuse) a per-thread connection to the SQLite database."""
        conn = getattr(DatabaseManager._tls, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            DatabaseManager._tls.conn = conn
        return conn

    def close(self):
        """Close the current thread's database connection."""
        conn = getattr(DatabaseManager._tls, "conn", None)
        if conn:
            conn.close()
            DatabaseManager._tls.conn = None

    def _get_table_columns(self, table_name: str) -> set:
        """Return the set of column names for a table (cached per instance)."""
        cache = getattr(self, "_col_cache", None)
        if cache is None:
            self._col_cache = {}
            cache = self._col_cache
        if table_name not in cache:
            conn = self.connect()
            cur = conn.execute(f'PRAGMA table_info("{table_name}")')
            cache[table_name] = {row[1] for row in cur.fetchall()}
        return cache[table_name]

    def _filter(self, table_name: str, data: dict) -> dict:
        """Strip keys that don't exist as columns in the target table."""
        cols = self._get_table_columns(table_name)
        return {k: v for k, v in data.items() if k in cols}

    # ── Initialization ───────────────────────────────────────────────────────

    def initialize_database(self):
        """Create all tables and the sync_log table if they don't exist."""
        conn = self.connect()
        conn.executescript(TABLES_SQL)
        conn.executescript(SYNC_LOG_TABLE_SQL)
        conn.commit()

    # ── Generic CRUD with sync tracking ──────────────────────────────────────

    def insert(self, table_name, data: dict, track_sync=True):
        conn = self.connect()
        if "id" not in data:
            data["id"] = new_uuid()
        if "created_on" not in data:
            data["created_on"] = utc_now()

        data = self._filter(table_name, data)

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        conn.execute(
            f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})',
            list(data.values()),
        )
        conn.commit()

        if track_sync:
            add_sync_log(conn, table_name, data["id"], SyncAction.INSERT, data)

        return data["id"]

    def update(self, table_name, record_id, data: dict, track_sync=True):
        conn = self.connect()
        data["modified_on"] = utc_now()
        data = self._filter(table_name, data)
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        conn.execute(
            f'UPDATE "{table_name}" SET {set_clause} WHERE id = ?',
            list(data.values()) + [record_id],
        )
        conn.commit()

        if track_sync:
            add_sync_log(conn, table_name, record_id, SyncAction.UPDATE, data)

    def soft_delete(self, table_name, record_id, deleted_by="", track_sync=True):
        """Soft-delete a row (set is_deleted = 1) and log it."""
        conn = self.connect()
        now = utc_now()
        conn.execute(
            f'UPDATE "{table_name}" SET is_deleted = 1, deleted_by = ?, deleted_on = ? WHERE id = ?',
            (deleted_by, now, record_id),
        )
        conn.commit()

        if track_sync:
            add_sync_log(
                conn,
                table_name,
                record_id,
                SyncAction.SOFT_DELETE,
                {"deleted_by": deleted_by, "deleted_on": now},
            )

    def hard_delete(self, table_name, record_id, track_sync=True):
        """Permanently delete a row and log it."""
        conn = self.connect()

        # Capture the row before deletion for sync purposes
        row_data = None
        if track_sync:
            row_data = self.get_by_id(table_name, record_id)

        conn.execute(
            f'DELETE FROM "{table_name}" WHERE id = ?',
            (record_id,),
        )
        conn.commit()

        if track_sync:
            add_sync_log(conn, table_name, record_id, SyncAction.HARD_DELETE, row_data)

    # ── Query helpers ────────────────────────────────────────────────────────

    def get_by_id(self, table_name, record_id):
        """Fetch a single row by id as a dict (or None)."""
        conn = self.connect()
        cursor = conn.execute(
            f'SELECT * FROM "{table_name}" WHERE id = ?', (record_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    def get_all(self, table_name, include_deleted=False):
        """Fetch all rows from a table as a list of dicts."""
        conn = self.connect()
        query = f'SELECT * FROM "{table_name}"'
        if not include_deleted:
            query += " WHERE is_deleted = 0 OR is_deleted IS NULL"
        cursor = conn.execute(query)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def query(self, sql, params=None):
        """Run an arbitrary SELECT and return rows as list of dicts."""
        conn = self.connect()
        cursor = conn.execute(sql, params or [])
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def execute(self, sql, params=None):
        """Run an arbitrary write statement (INSERT/UPDATE/DELETE)."""
        conn = self.connect()
        conn.execute(sql, params or [])
        conn.commit()
