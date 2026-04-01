"""
ORM Session & Repository – engine setup and a generic typed repository.

The engine reuses the same SQLite file as DatabaseManager so no data is
duplicated – you can mix raw-SQL helpers and ORM calls freely.

Typical usage
─────────────
from Database.orm_session import get_session, Repository
from Database.orm_models import Company, Ledger

# --- context-manager style (auto-commit / rollback) -----------------------
with get_session() as session:
    repo = Repository(session, Company)

    # Create
    company = repo.add(Company(name="Acme Ltd", email="acme@example.com",
                                state="MH", state_code="27", gstin="",
                                country="India", logo_url="", currency="INR"))

    # Read by PK
    c = repo.get(company.id)

    # List all active
    active = repo.list_active(company_id="...")

    # Update
    c.name = "Acme Corp"
    session.commit()          # or rely on the context-manager auto-commit

    # Soft-delete
    repo.soft_delete(c.id, deleted_by="user@example.com")

    # Hard-delete
    repo.hard_delete(c.id)
"""

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generic, Iterator, List, Optional, Type, TypeVar

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from Database.orm_models import Base

# ─── Engine setup ────────────────────────────────────────────────────────────

_DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
_DB_PATH = os.path.join(_DB_DIR, "accounting.db")

os.makedirs(_DB_DIR, exist_ok=True)

_engine = create_engine(
    f"sqlite:///{_DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)

# WAL mode + foreign keys enabled for every new connection
from sqlalchemy import event as _sa_event


@_sa_event.listens_for(_engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


_SessionFactory = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)


def create_all_tables() -> None:
    """Create any missing ORM-managed tables (idempotent)."""
    Base.metadata.create_all(_engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """
    Yield a SQLAlchemy Session.  Commits on clean exit, rolls back on error.

    Example::

        with get_session() as session:
            session.add(Company(name="Test"))
    """
    session: Session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ─── Generic Repository ───────────────────────────────────────────────────────

T = TypeVar("T")


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


class Repository(Generic[T]):
    """
    Thin typed wrapper around a Session for a single model class.

    Parameters
    ----------
    session : Session
        An open SQLAlchemy session (e.g. from ``get_session()``).
    model : Type[T]
        The ORM model class (e.g. ``Company``, ``Ledger``).
    """

    def __init__(self, session: Session, model: Type[T]) -> None:
        self._session = session
        self._model = model

    # ── Create ────────────────────────────────────────────────────────────────

    def add(self, instance: T) -> T:
        """Persist a new model instance.  Does NOT commit – call session.commit()."""
        self._session.add(instance)
        self._session.flush()   # populate server-generated defaults into the object
        return instance

    # ── Read ──────────────────────────────────────────────────────────────────

    def get(self, record_id: str) -> Optional[T]:
        """Return the row with the given primary key, or None."""
        return self._session.get(self._model, record_id)

    def list_all(self, include_deleted: bool = False) -> List[T]:
        """
        Return all rows.  When *include_deleted* is False (default) rows with
        ``is_deleted = 1`` are excluded (if the model has that column).
        """
        stmt = select(self._model)
        if not include_deleted and hasattr(self._model, "is_deleted"):
            stmt = stmt.where(self._model.is_deleted == 0)
        return list(self._session.scalars(stmt).all())

    def list_active(self, company_id: str, include_deleted: bool = False) -> List[T]:
        """
        Return rows filtered by *company_id* (if the model has that column).
        Falls back to :meth:`list_all` if the column is absent.
        """
        stmt = select(self._model)
        if hasattr(self._model, "company_id"):
            stmt = stmt.where(self._model.company_id == company_id)
        if not include_deleted and hasattr(self._model, "is_deleted"):
            stmt = stmt.where(self._model.is_deleted == 0)
        return list(self._session.scalars(stmt).all())

    def find(self, **filters) -> List[T]:
        """
        Filter rows by keyword arguments matching column names.

        Example::

            repo.find(type="SaleInvoice", status="Posted")
        """
        stmt = select(self._model)
        for column_name, value in filters.items():
            col = getattr(self._model, column_name, None)
            if col is not None:
                stmt = stmt.where(col == value)
        return list(self._session.scalars(stmt).all())

    def first(self, **filters) -> Optional[T]:
        """Return the first matching row or None."""
        results = self.find(**filters)
        return results[0] if results else None

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, record_id: str, **fields) -> Optional[T]:
        """
        Bulk-update columns on the row identified by *record_id*.
        ``modified_on`` is set automatically when the model supports it.

        Returns the updated instance, or None if not found.
        """
        instance = self.get(record_id)
        if instance is None:
            return None
        if hasattr(instance, "modified_on"):
            fields.setdefault("modified_on", _utc_now())
        for key, value in fields.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self._session.flush()
        return instance

    # ── Delete ────────────────────────────────────────────────────────────────

    def soft_delete(self, record_id: str, deleted_by: str = "") -> bool:
        """
        Mark the row as deleted (``is_deleted = 1``) without removing it.
        Returns True if the row was found, False otherwise.
        """
        instance = self.get(record_id)
        if instance is None:
            return False
        now = _utc_now()
        if hasattr(instance, "is_deleted"):
            instance.is_deleted = 1
        if hasattr(instance, "deleted_by"):
            instance.deleted_by = deleted_by
        if hasattr(instance, "deleted_on"):
            instance.deleted_on = now
        self._session.flush()
        return True

    def hard_delete(self, record_id: str) -> bool:
        """
        Permanently remove the row from the database.
        Returns True if the row was found, False otherwise.
        """
        instance = self.get(record_id)
        if instance is None:
            return False
        self._session.delete(instance)
        self._session.flush()
        return True
