"""
PostgreSQL cloud configuration and table/column name mapping.
Maps between cloud PG (PascalCase EF Core) and local SQLite (snake_case).
"""

import re
import decimal
import uuid

# ── Cloud PostgreSQL Connection ──────────────────────────────────────────────

PG_CONFIG = {
    "host": "147.79.66.51",
    "database": "AowCloud1",
    "user": "dbadmin",
    "password": "dbadmin#1",
    "port": 5432,
    "connect_timeout": 15,
}

# ── Table Name Mapping: PG (EF Core DbSet) -> Local SQLite ──────────────────
# Keys are the exact PostgreSQL table names (matching EF Core DbSet names).

PG_TO_LOCAL_TABLE = {
    "Companies":                "company",
    "UserCompanies":            "user_company",
    "FinancialYears":           "financial_year",
    "CompanyFeatures":          "company_feature",
    "CompanyRoles":             "company_role",
    "CompanyRoleFeatures":      "company_role_feature",
    "UserCompanyRoleFeatures":  "user_company_role_feature",
    "CompanyRecharges":         "company_recharge",
    "Ledgers":                  "ledger",
    "LedgerOpeningBalances":    "ledger_opening_balance",
    "Taxes":                    "tax",
    "TaxComponents":            "tax_component",
    "TaxRates":                 "tax_rate",
    "Attributes":               "attribute",
    "AttributeOptions":         "attribute_option",
    "Products":                 "product",
    "ProductAttributes":        "product_attribute",
    "ProductVariants":          "product_variant",
    "ProductVariantAttributes": "product_variant_attribute",
    "ProductOpeningStocks":     "product_opening_stock",
    "Transactions":             "transaction",
    "TransactionLedgers":       "transaction_ledger",
    "TransactionItems":         "transaction_item",
    "TransactionItemVariants":  "transaction_item_variant",
    "TransactionTaxes":         "transaction_tax",
    "TransactionPayments":      "transaction_payment",
    "TransactionLinks":         "transaction_link",
    "TransactionTypeSettings":  "transaction_type_settings",
}

# Reverse mapping for push-to-cloud
LOCAL_TO_PG_TABLE = {v: k for k, v in PG_TO_LOCAL_TABLE.items()}


# ── Column Name Conversion ──────────────────────────────────────────────────

def pascal_to_snake(name: str) -> str:
    """Convert PascalCase / camelCase to snake_case."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    # Abbreviation-style column names that don't round-trip through
    # pascal_to_snake → snake_to_pascal.  Keys are the snake_case form
    # produced by pascal_to_snake; values are the original PG column names.
    _OVERRIDES = {
        "gstin": "GSTIN",
        "ifsc_code": "IFSCCode",
        "hsn_code": "HSNCode",
        "sku": "SKU",
    }
    override = _OVERRIDES.get(name)
    if override:
        return override
    return "".join(part.capitalize() for part in name.split("_"))


def convert_pg_row_to_local(pg_columns: list[str], row: tuple) -> dict:
    """Convert a PG row (PascalCase columns) to a local dict (snake_case keys)."""
    result = {}
    for col, val in zip(pg_columns, row):
        local_col = pascal_to_snake(col)
        # Convert Python booleans to SQLite integers
        if isinstance(val, bool):
            val = 1 if val else 0
        # Convert Decimal to float (SQLite doesn't support decimal.Decimal)
        elif isinstance(val, decimal.Decimal):
            val = float(val)
        # Convert UUID to string (SQLite doesn't support uuid.UUID)
        elif isinstance(val, uuid.UUID):
            val = str(val)
        result[local_col] = val
    return result
