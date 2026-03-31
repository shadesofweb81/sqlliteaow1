"""
Sync Log module for offline-first sync tracking.
Every INSERT, UPDATE, soft-delete, or hard-delete on the local SQLite database
is recorded in the sync_log table. When the user pushes to the cloud PostgreSQL
database, this log is replayed against the remote DB.
"""

from Database.models import new_uuid, utc_now


class SyncAction:
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    SOFT_DELETE = "SOFT_DELETE"
    HARD_DELETE = "HARD_DELETE"


SYNC_LOG_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sync_log (
    id TEXT PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    action TEXT NOT NULL,           -- INSERT | UPDATE | SOFT_DELETE | HARD_DELETE
    changed_data TEXT,              -- JSON snapshot of changed fields
    created_on TEXT NOT NULL,
    is_synced INTEGER DEFAULT 0,
    synced_on TEXT,
    sync_error TEXT,
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_sync_log_is_synced ON sync_log(is_synced);
CREATE INDEX IF NOT EXISTS idx_sync_log_table ON sync_log(table_name);
CREATE INDEX IF NOT EXISTS idx_sync_log_record ON sync_log(record_id);
"""


def add_sync_log(conn, table_name, record_id, action, changed_data=None):
    """Insert a new entry into sync_log."""
    import json
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO sync_log (id, table_name, record_id, action, changed_data, created_on)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            new_uuid(),
            table_name,
            record_id,
            action,
            json.dumps(changed_data) if changed_data else None,
            utc_now(),
        ),
    )
    conn.commit()


def get_pending_sync_logs(conn):
    """Return all unsynced log entries ordered by creation time."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sync_log WHERE is_synced = 0 ORDER BY created_on ASC"
    )
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def mark_synced(conn, sync_log_id):
    """Mark a sync_log entry as successfully synced."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sync_log SET is_synced = 1, synced_on = ? WHERE id = ?",
        (utc_now(), sync_log_id),
    )
    conn.commit()


def mark_sync_error(conn, sync_log_id, error_message):
    """Record a sync error and increment retry count."""
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE sync_log
           SET sync_error = ?, retry_count = retry_count + 1
           WHERE id = ?""",
        (error_message, sync_log_id),
    )
    conn.commit()
