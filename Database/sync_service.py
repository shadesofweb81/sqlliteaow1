"""
Sync Service – pushes pending local changes to the cloud PostgreSQL database.

Algorithm
---------
1. Load all unsynced local sync_log rows.
2. Query cloud SyncLogs for any IDs that already exist (a previous partial push).
3. For each new entry:
   a. Apply the data change to the relevant cloud table (INSERT / UPDATE / DELETE).
   b. Mirror the sync_log row into cloud SyncLogs so both sides stay consistent.
   c. Mark the local row as synced.
4. On error, record the error in the local sync_log row and continue.
"""

import asyncio
import json
import uuid as _uuid_mod

import psycopg2
import psycopg2.extras

from Database.db_manager import DatabaseManager
from Database.sync_log import (
    SyncAction,
    get_pending_sync_logs,
    mark_sync_error,
    mark_synced,
)
from Services.pg_config import LOCAL_TO_PG_TABLE, PG_CONFIG, snake_to_pascal

# Register psycopg2 UUID adapter so uuid.UUID objects are sent as PG uuid type
psycopg2.extras.register_uuid()


def _as_uuid(value):
    """Return a uuid.UUID if *value* is a valid UUID string, otherwise return it unchanged."""
    if isinstance(value, str):
        try:
            return _uuid_mod.UUID(value)
        except ValueError:
            pass
    return value


def _prepare_row(mapping: dict) -> dict:
    """Convert any UUID-shaped string values to uuid.UUID objects for psycopg2 adaptation."""
    return {k: _as_uuid(v) for k, v in mapping.items()}


class SyncService:
    """Static async helpers – mirrors PullService structure for UI integration."""

    # ── Public async entry-point ──────────────────────────────────────────────

    @staticmethod
    async def push_to_cloud(progress_callback=None):
        """Run the blocking push in a thread executor so the UI stays responsive.

        Returns:
            (success: bool, message: str)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, SyncService._sync_push_to_cloud, progress_callback
        )

    # ── Blocking implementation ───────────────────────────────────────────────

    @staticmethod
    def _sync_push_to_cloud(progress_callback=None):
        def _progress(msg):
            if progress_callback:
                progress_callback(msg)

        local_conn = None
        pg_conn = None
        try:
            local_conn = DatabaseManager().connect()
            pending = get_pending_sync_logs(local_conn)
            if not pending:
                return True, "Nothing to push – all changes are up to date."

            _progress(f"Found {len(pending)} pending change(s). Connecting to cloud…")
            pg_conn = psycopg2.connect(**PG_CONFIG)
            pg_cursor = pg_conn.cursor()

            # ── Compare: skip entries already present in cloud SyncLogs ──────
            pending_ids = [e["id"] for e in pending]
            pg_cursor.execute(
                'SELECT "Id" FROM "SyncLogs" WHERE "Id" = ANY(%s::uuid[])',
                (pending_ids,),
            )
            already_in_cloud = {row[0] for row in pg_cursor.fetchall()}
            _progress(
                f"{len(already_in_cloud)} already in cloud. "
                f"Pushing {len(pending) - len(already_in_cloud)} new change(s)…"
            )

            success = 0
            errors = 0

            for entry in pending:
                if entry["id"] in already_in_cloud:
                    # Change was pushed previously; just mark as synced locally.
                    mark_synced(local_conn, entry["id"])
                    success += 1
                    continue

                try:
                    SyncService._apply_to_postgres(pg_cursor, entry)
                    SyncService._insert_cloud_sync_log(pg_cursor, entry)
                    pg_conn.commit()
                    mark_synced(local_conn, entry["id"])
                    success += 1
                    _progress(
                        f"  ✓ {entry['action']} {entry['table_name']} "
                        f"({entry['record_id'][:8]}…)"
                    )
                except Exception as exc:
                    pg_conn.rollback()
                    mark_sync_error(local_conn, entry["id"], str(exc))
                    errors += 1
                    _progress(f"  ✗ {entry['action']} {entry['table_name']}: {exc}")

            if errors:
                return (
                    False,
                    f"Push complete: {success} succeeded, {errors} failed. "
                    "Check sync log for details.",
                )
            return True, f"Push complete: {success} change(s) pushed to cloud."

        except Exception as exc:
            return False, f"Push failed: {exc}"
        finally:
            if pg_conn:
                pg_conn.close()
            if local_conn:
                local_conn.close()

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _apply_to_postgres(pg_cursor, log_entry):
        """Translate one local sync_log entry into a PostgreSQL statement."""
        local_table = log_entry["table_name"]
        record_id   = log_entry["record_id"]
        action      = log_entry["action"]
        changed_data = (
            json.loads(log_entry["changed_data"]) if log_entry["changed_data"] else {}
        )

        # Map local snake_case table name → cloud PascalCase table name
        pg_table = LOCAL_TO_PG_TABLE.get(local_table, snake_to_pascal(local_table) + "s")
        uid = _as_uuid(record_id)

        if action == SyncAction.INSERT:
            # changed_data is flat {snake_col: value}
            pg_cols = _prepare_row({snake_to_pascal(k): v for k, v in changed_data.items()})
            cols_sql     = ", ".join(f'"{c}"' for c in pg_cols)
            placeholders = ", ".join(["%s"] * len(pg_cols))
            pg_cursor.execute(
                f'INSERT INTO "{pg_table}" ({cols_sql}) VALUES ({placeholders}) '
                f'ON CONFLICT ("Id") DO NOTHING',
                list(pg_cols.values()),
            )

        elif action == SyncAction.UPDATE:
            # changed_data format: {snake_col: {"old": x, "new": y}}
            updates = {}
            for k, v in changed_data.items():
                new_val = v["new"] if isinstance(v, dict) and "new" in v else v
                updates[snake_to_pascal(k)] = _as_uuid(new_val)
            set_clause = ", ".join(f'"{col}" = %s' for col in updates)
            pg_cursor.execute(
                f'UPDATE "{pg_table}" SET {set_clause} WHERE "Id" = %s',
                list(updates.values()) + [uid],
            )

        elif action == SyncAction.SOFT_DELETE:
            pg_cursor.execute(
                f'UPDATE "{pg_table}" SET "IsDeleted" = true, "DeletedBy" = %s, '
                f'"DeletedOn" = %s WHERE "Id" = %s',
                (
                    changed_data.get("deleted_by", ""),
                    changed_data.get("deleted_on"),
                    uid,
                ),
            )

        elif action == SyncAction.HARD_DELETE:
            pg_cursor.execute(
                f'DELETE FROM "{pg_table}" WHERE "Id" = %s',
                (uid,),
            )

    @staticmethod
    def _insert_cloud_sync_log(pg_cursor, log_entry):
        """Mirror the local sync_log row into the cloud SyncLogs table."""
        pg_cursor.execute(
            """
            INSERT INTO "SyncLogs"
                ("Id", "TableName", "RecordId", "Action", "ChangedData",
                 "CreatedOn", "IsSynced", "RetryCount")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ("Id") DO NOTHING
            """,
            (
                _as_uuid(log_entry["id"]),
                log_entry["table_name"],
                _as_uuid(log_entry["record_id"]),
                log_entry["action"],
                log_entry["changed_data"],
                log_entry["created_on"],
                True,                          # already applied → synced on cloud
                log_entry.get("retry_count", 0),
            ),
        )
