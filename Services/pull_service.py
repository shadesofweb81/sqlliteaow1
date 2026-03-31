"""
Pull Service – pulls data from cloud PostgreSQL into local SQLite.
All queries are parameterised and scoped to the logged-in user's companies.
"""

import asyncio
import psycopg2
import psycopg2.extras
from Database.db_manager import DatabaseManager
from Services.session import Session
from Services.pg_config import (
    PG_CONFIG,
    PG_TO_LOCAL_TABLE,
    convert_pg_row_to_local,
)


# Tables that hang directly off a Company (filtered by CompanyId)
# Order matters: parent tables must come before their dependents.
_COMPANY_SCOPED_PG_TABLES = [
    "FinancialYears",           # → company
    "CompanyRecharges",         # → company
    "CompanyRoles",             # → company
    "Taxes",                    # → company  (must precede Ledgers)
    "Ledgers",                  # → company, tax_entity_id → tax
    "Attributes",               # → company
    "AttributeOptions",         # → attribute, company
    "Products",                 # → company  (parent_id self-ref, handled by FK-off)
    "ProductAttributes",        # → product, attribute, company
    "ProductVariants",          # → product, company
    "ProductVariantAttributes", # → product_variant, attribute, attribute_option, company
    "TransactionTypeSettings",  # → company
    "Transactions",             # → company, financial_year
]

# Tables requiring a JOIN through a parent to scope by company
_JOIN_PG_TABLES = [
    "LedgerOpeningBalances",
    "TaxComponents",
    "TaxRates",
    "ProductOpeningStocks",
    "TransactionLedgers",
    "TransactionItems",
    "TransactionTaxes",
    "TransactionPayments",
    "TransactionLinks",
    "TransactionItemVariants",
]

# Role/feature tables scoped by CompanyId
_ROLE_FEATURE_PG_TABLES = [
    "CompanyRoleFeatures",
    # UserCompanyRoleFeatures has no CompanyId – pulled via JOIN below
]


class PullService:

    @staticmethod
    async def pull_all(progress_callback=None):
        """Pull user-scoped data from cloud PG to local SQLite.

        Args:
            progress_callback: Optional callable(message: str) for UI updates.

        Returns:
            (success: bool, message: str)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, PullService._sync_pull_all, progress_callback
        )

    @staticmethod
    async def pull_company(company_id: str, progress_callback=None):
        """Pull all data for a single company by its ID.

        Returns:
            (success: bool, message: str)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, PullService._sync_pull_company, company_id, progress_callback
        )

    @staticmethod
    def _sync_pull_all(progress_callback=None):
        def _progress(msg):
            if progress_callback:
                progress_callback(msg)

        user = Session.get_user()
        if not user:
            return False, "Not logged in."

        user_id = user.id
        pg_conn = None

        try:
            _progress("Connecting to cloud database…")
            pg_conn = psycopg2.connect(**PG_CONFIG)
            pg_cursor = pg_conn.cursor()

            db = DatabaseManager()
            # Disable FK enforcement for the bulk pull – data comes from a
            # trusted cloud source and self-referential tables (ledger, product)
            # cannot be topologically sorted.  Re-enabled in the finally block.
            db.connect().execute("PRAGMA foreign_keys=OFF")

            # ── 1. Fetch UserCompanies rows (collect only, don't insert yet) ──
            _progress("Fetching user companies…")
            pg_cursor.execute(
                'SELECT * FROM "UserCompanies" WHERE "UserId" = %s',
                (user_id,),
            )
            uc_columns = [desc[0] for desc in pg_cursor.description]
            uc_rows = [
                convert_pg_row_to_local(uc_columns, row)
                for row in pg_cursor.fetchall()
            ]

            company_ids = [r["company_id"] for r in uc_rows]
            if not company_ids:
                return True, "No companies found for this user."

            # ── 2. Pull Companies first (satisfies user_company FK) ──────
            _progress("Pulling companies…")
            _pull_by_ids(pg_cursor, db, "Companies", '"Id"', company_ids)

            # ── 3. Now safe to upsert UserCompanies ──────────────────────
            _progress("Pulling user companies…")
            for local in uc_rows:
                _upsert(db, "user_company", local)

            # ── TODO: remaining tables (testing mode) ────────────────────
            # ── 4. Pull CompanyFeatures (global, no company filter) ──────
            # ── 5. Company-scoped tables ─────────────────────────────────
            # ── 6. Join-based tables (no direct CompanyId) ───────────────
            # ── 7. Role/feature tables ───────────────────────────────────

            _progress("Pull complete.")
            return True, f"Synced {len(company_ids)} company(ies) from cloud."

        except psycopg2.OperationalError as e:
            return False, f"Database connection error: {e}"
        except Exception as e:
            return False, f"Pull failed: {e}"
        finally:
            # Always re-enable FK enforcement
            try:
                DatabaseManager().connect().execute("PRAGMA foreign_keys=ON")
            except Exception:
                pass
            if pg_conn:
                pg_conn.close()

    @staticmethod
    def _sync_pull_company(company_id: str, progress_callback=None):
        def _progress(msg):
            if progress_callback:
                progress_callback(msg)

        pg_conn = None
        company_ids = [company_id]

        try:
            _progress("Connecting to cloud database…")
            pg_conn = psycopg2.connect(**PG_CONFIG)
            pg_cursor = pg_conn.cursor()

            db = DatabaseManager()
            db.connect().execute("PRAGMA foreign_keys=OFF")

            # ── Company row itself ───────────────────────────────────────
            _progress("Pulling company…")
            _pull_by_ids(pg_cursor, db, "Companies", '"Id"', company_ids)

            # ── CompanyFeatures (global) ─────────────────────────────────
            _progress("Pulling company features…")
            pg_cursor.execute('SELECT * FROM "CompanyFeatures"')
            cf_cols = [desc[0] for desc in pg_cursor.description]
            for row in pg_cursor.fetchall():
                local = convert_pg_row_to_local(cf_cols, row)
                _upsert(db, "company_feature", local)

            # ── Company-scoped tables ────────────────────────────────────
            for pg_table in _COMPANY_SCOPED_PG_TABLES:
                local_table = PG_TO_LOCAL_TABLE[pg_table]
                _progress(f"Pulling {local_table}…")
                _pull_by_ids(pg_cursor, db, pg_table, '"CompanyId"', company_ids)

            # ── Join-based child tables ──────────────────────────────────
            for pg_table in _JOIN_PG_TABLES:
                local_table = PG_TO_LOCAL_TABLE[pg_table]
                _progress(f"Pulling {local_table}…")
                _pull_via_join(pg_cursor, db, pg_table, local_table, company_ids)

            # ── Role / feature tables ────────────────────────────────────
            for pg_table in _ROLE_FEATURE_PG_TABLES:
                local_table = PG_TO_LOCAL_TABLE[pg_table]
                _progress(f"Pulling {local_table}…")
                _pull_by_ids(pg_cursor, db, pg_table, '"CompanyId"', company_ids)
            # UserCompanyRoleFeatures has no CompanyId – JOIN through CompanyRoleFeatures
            _progress("Pulling user_company_role_feature…")
            _pull_via_join(pg_cursor, db, "UserCompanyRoleFeatures", "user_company_role_feature", company_ids)
            _progress("Company data synced.")
            return True, "Company data synced successfully."

        except psycopg2.OperationalError as e:
            return False, f"Database connection error: {e}"
        except Exception as e:
            return False, f"Pull failed: {e}"
        finally:
            try:
                DatabaseManager().connect().execute("PRAGMA foreign_keys=ON")
            except Exception:
                pass
            if pg_conn:
                pg_conn.close()


# ── Internal Helpers ─────────────────────────────────────────────────────────

def _pull_by_ids(pg_cursor, db: DatabaseManager, pg_table: str, id_column: str, ids: list):
    """SELECT * FROM pg_table WHERE id_column IN (...) using parameterised query."""
    if not ids:
        return
    placeholders = ",".join(["%s"] * len(ids))
    pg_cursor.execute(
        f'SELECT * FROM "{pg_table}" WHERE {id_column} IN ({placeholders})',
        ids,
    )
    columns = [desc[0] for desc in pg_cursor.description]
    local_table = PG_TO_LOCAL_TABLE[pg_table]
    for row in pg_cursor.fetchall():
        local = convert_pg_row_to_local(columns, row)
        _upsert(db, local_table, local)


def _pull_via_join(pg_cursor, db: DatabaseManager, pg_table: str, local_table: str, company_ids: list):
    """Pull rows from tables that lack CompanyId by JOINing through their parent."""
    if not company_ids:
        return

    placeholders = ",".join(["%s"] * len(company_ids))

    # Define the JOIN query per table
    join_queries = {
        "LedgerOpeningBalances": (
            f'SELECT lob.* FROM "LedgerOpeningBalances" lob '
            f'INNER JOIN "Ledgers" l ON lob."LedgerId" = l."Id" '
            f'WHERE l."CompanyId" IN ({placeholders})'
        ),
        "TaxComponents": (
            f'SELECT tc.* FROM "TaxComponents" tc '
            f'INNER JOIN "Taxes" t ON tc."TaxId" = t."Id" '
            f'WHERE t."CompanyId" IN ({placeholders})'
        ),
        "TaxRates": (
            f'SELECT tr.* FROM "TaxRates" tr '
            f'INNER JOIN "Taxes" t ON tr."TaxId" = t."Id" '
            f'WHERE t."CompanyId" IN ({placeholders})'
        ),
        "ProductOpeningStocks": (
            f'SELECT pos.* FROM "ProductOpeningStocks" pos '
            f'INNER JOIN "Products" p ON pos."ProductId" = p."Id" '
            f'WHERE p."CompanyId" IN ({placeholders})'
        ),
        "TransactionLedgers": (
            f'SELECT tl.* FROM "TransactionLedgers" tl '
            f'INNER JOIN "Transactions" t ON tl."TransactionId" = t."Id" '
            f'WHERE t."CompanyId" IN ({placeholders})'
        ),
        "TransactionItems": (
            f'SELECT ti.* FROM "TransactionItems" ti '
            f'INNER JOIN "Transactions" t ON ti."TransactionId" = t."Id" '
            f'WHERE t."CompanyId" IN ({placeholders})'
        ),
        "TransactionTaxes": (
            f'SELECT tt.* FROM "TransactionTaxes" tt '
            f'INNER JOIN "Transactions" t ON tt."TransactionId" = t."Id" '
            f'WHERE t."CompanyId" IN ({placeholders})'
        ),
        "TransactionPayments": (
            f'SELECT tp.* FROM "TransactionPayments" tp '
            f'INNER JOIN "Transactions" t ON tp."PaymentTransactionId" = t."Id" '
            f'WHERE t."CompanyId" IN ({placeholders})'
        ),
        "TransactionLinks": (
            f'SELECT tl.* FROM "TransactionLinks" tl '
            f'INNER JOIN "Transactions" t ON tl."FromTransactionId" = t."Id" '
            f'WHERE t."CompanyId" IN ({placeholders})'
        ),
        "TransactionItemVariants": (
            f'SELECT tiv.* FROM "TransactionItemVariants" tiv '
            f'INNER JOIN "TransactionItems" ti ON tiv."TransactionItemId" = ti."Id" '
            f'INNER JOIN "Transactions" t ON ti."TransactionId" = t."Id" '
            f'WHERE t."CompanyId" IN ({placeholders})'
        ),
        "UserCompanyRoleFeatures": (
            f'SELECT ucrf.* FROM "UserCompanyRoleFeatures" ucrf '
            f'INNER JOIN "CompanyRoleFeatures" crf ON ucrf."CompanyRoleFeatureId" = crf."Id" '
            f'WHERE crf."CompanyId" IN ({placeholders})'
        ),
    }

    query = join_queries.get(pg_table)
    if not query:
        return

    pg_cursor.execute(query, company_ids)
    columns = [desc[0] for desc in pg_cursor.description]
    for row in pg_cursor.fetchall():
        local = convert_pg_row_to_local(columns, row)
        _upsert(db, local_table, local)


def _upsert(db: DatabaseManager, local_table: str, data: dict):
    """INSERT or UPDATE a row in the local SQLite database (no sync tracking)."""
    record_id = data.get("id")
    if not record_id:
        return

    existing = db.get_by_id(local_table, record_id)
    if existing:
        db.update(local_table, record_id, data, track_sync=False)
    else:
        db.insert(local_table, data, track_sync=False)
