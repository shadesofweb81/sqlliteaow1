"""
Sync Service – pushes pending local changes to the cloud PostgreSQL database.
"""

import json
from Database.sync_log import get_pending_sync_logs, mark_synced, mark_sync_error, SyncAction


class SyncService:
    """Reads unsynced entries from sync_log and applies them to the remote DB."""

    def __init__(self, pg_connection_factory):
        """
        Args:
            pg_connection_factory: A callable that returns a psycopg2 connection
                                   to the cloud PostgreSQL database.
        """
        self.pg_connection_factory = pg_connection_factory

    def push_to_cloud(self, local_conn):
        """Push all pending sync_log entries to the cloud database.

        Args:
            local_conn: The local SQLite connection (to read sync_log).

        Returns:
            Tuple of (success_count, error_count).
        """
        pending = get_pending_sync_logs(local_conn)
        if not pending:
            return 0, 0

        success = 0
        errors = 0
        pg_conn = None

        try:
            pg_conn = self.pg_connection_factory()
            pg_cursor = pg_conn.cursor()

            for log_entry in pending:
                try:
                    self._apply_to_postgres(pg_cursor, log_entry)
                    pg_conn.commit()
                    mark_synced(local_conn, log_entry["id"])
                    success += 1
                except Exception as e:
                    pg_conn.rollback()
                    mark_sync_error(local_conn, log_entry["id"], str(e))
                    errors += 1
        finally:
            if pg_conn:
                pg_conn.close()

        return success, errors

    def _apply_to_postgres(self, pg_cursor, log_entry):
        """Apply a single sync_log entry to PostgreSQL."""
        table = log_entry["table_name"]
        record_id = log_entry["record_id"]
        action = log_entry["action"]
        changed_data = json.loads(log_entry["changed_data"]) if log_entry["changed_data"] else {}

        if action == SyncAction.INSERT:
            columns = ", ".join(changed_data.keys())
            placeholders = ", ".join(["%s"] * len(changed_data))
            pg_cursor.execute(
                f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders}) '
                f"ON CONFLICT (id) DO NOTHING",
                list(changed_data.values()),
            )

        elif action == SyncAction.UPDATE:
            set_clause = ", ".join([f"{k} = %s" for k in changed_data.keys()])
            pg_cursor.execute(
                f'UPDATE "{table}" SET {set_clause} WHERE id = %s',
                list(changed_data.values()) + [record_id],
            )

        elif action == SyncAction.SOFT_DELETE:
            pg_cursor.execute(
                f'UPDATE "{table}" SET is_deleted = true, deleted_by = %s, deleted_on = %s WHERE id = %s',
                (changed_data.get("deleted_by", ""), changed_data.get("deleted_on"), record_id),
            )

        elif action == SyncAction.HARD_DELETE:
            pg_cursor.execute(
                f'DELETE FROM "{table}" WHERE id = %s',
                (record_id,),
            )
