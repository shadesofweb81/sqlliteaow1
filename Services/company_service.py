"""
Company Service – SQLAlchemy-backed queries for company data.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as SASession

from Database.db_manager import DatabaseManager
from Database.orm_models import Company, UserCompany
from Database.orm_session import get_session
from Database.sync_log import SyncAction, add_sync_log


_EDITABLE_FIELDS = [
    "name", "gstin", "phone", "email", "website", "currency", "tax_id",
    "address", "city", "state", "state_code", "zip_code", "country",
    "bank_name", "account_number", "ifsc_code", "account_holder_name",
    "branch_name", "swift_code", "terms_and_conditions",
]


class CompanyService:

    @staticmethod
    def get_companies_for_user(user_id: str) -> list[dict]:
        """
        Return all companies linked to *user_id* via the user_company table.

        Each item in the returned list is a plain dict with the keys used by
        the UI (mirrors the columns fetched by the previous raw-SQL query).

        Returns an empty list when no companies are found.
        """
        with get_session() as session:
            stmt = (
                select(Company)
                .join(UserCompany, UserCompany.company_id == Company.id)
                .where(UserCompany.user_id == user_id)
                .order_by(Company.name.asc())
            )
            companies: list[Company] = list(session.scalars(stmt).all())
            return [CompanyService._to_dict(c) for c in companies]

    @staticmethod
    def get_by_id(company_id: str) -> dict | None:
        """Return a single company as a dict, or None if not found."""
        with get_session() as session:
            company = session.get(Company, company_id)
            if company is None:
                return None
            return CompanyService._to_dict(company)

    @staticmethod
    def update_company(company_id: str, data: dict) -> None:
        """Persist editable fields from *data* onto the company record and write a sync log row."""
        changed: dict = {}
        with get_session() as session:
            company = session.get(Company, company_id)
            if company is None:
                raise ValueError(f"Company {company_id!r} not found")
            for field in _EDITABLE_FIELDS:
                if field in data:
                    old_val = getattr(company, field, None)
                    new_val = data[field]
                    if old_val != new_val:
                        changed[field] = {"old": old_val, "new": new_val}
                    setattr(company, field, new_val)
            company.modified_on = datetime.utcnow().isoformat()
            session.commit()

        if changed:
            conn = DatabaseManager().connect()
            add_sync_log(conn, "company", company_id, SyncAction.UPDATE, changed)

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _to_dict(c: Company) -> dict:
        """Flatten an ORM Company instance into a plain dict for the UI."""
        return {
            "id":                   c.id,
            "name":                 c.name or "",
            "gstin":                c.gstin or "",
            "address":              c.address or "",
            "city":                 c.city or "",
            "state":                c.state or "",
            "state_code":           c.state_code or "",
            "zip_code":             c.zip_code or "",
            "country":              c.country or "",
            "phone":                c.phone or "",
            "email":                c.email or "",
            "website":              c.website or "",
            "currency":             c.currency or "INR",
            "tax_id":               c.tax_id or "",
            "bank_name":            c.bank_name or "",
            "account_number":       c.account_number or "",
            "ifsc_code":            c.ifsc_code or "",
            "account_holder_name":  c.account_holder_name or "",
            "branch_name":          c.branch_name or "",
            "swift_code":           c.swift_code or "",
            "terms_and_conditions": c.terms_and_conditions or "",
            "is_deleted":           c.is_deleted or 0,
        }
