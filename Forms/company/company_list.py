"""
Company list form – shows all companies linked to the logged-in user.
"""

import tkinter as tk
from tkinter import ttk
import traceback
from Database.db_manager import DatabaseManager
from Services.session import Session
from Forms.error_dialog import show_error


COLUMNS = [
    ("name",       "Company Name", 220),
    ("gstin",      "GSTIN",        150),
    ("city",       "City",         110),
    ("state",      "State",        110),
    ("phone",      "Phone",        120),
    ("email",      "Email",        180),
    ("currency",   "Currency",      80),
    ("is_deleted", "Deleted",       60),
]

BG = "#f4f6f9"


class CompanyListForm(tk.Frame):
    """Embeddable frame that lists companies for the current user."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._build_ui()
        self.load()

    # ── UI Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Title bar ─────────────────
        top = tk.Frame(self, bg=BG)
        top.pack(fill=tk.X, padx=24, pady=(20, 0))

        tk.Label(
            top, text="Companies",
            font=("Segoe UI", 16, "bold"),
            bg=BG,
        ).pack(side=tk.LEFT, anchor=tk.W)

        self.refresh_btn = ttk.Button(top, text="↻ Refresh", command=self.load)
        self.refresh_btn.pack(side=tk.RIGHT)

        ttk.Separator(self).pack(fill=tk.X, padx=24, pady=(8, 0))

        # ── Search bar ────────────────
        search_bar = tk.Frame(self, bg=BG)
        search_bar.pack(fill=tk.X, padx=24, pady=(10, 6))

        tk.Label(search_bar, text="Search:", bg=BG).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        ttk.Entry(search_bar, textvariable=self.search_var, width=30).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        self.count_lbl = tk.Label(search_bar, text="", bg=BG, fg="#888", font=("Segoe UI", 9))
        self.count_lbl.pack(side=tk.RIGHT)

        # ── Treeview ──────────────────
        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))

        cols = [c[0] for c in COLUMNS]
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT,  fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        for col_id, heading, width in COLUMNS:
            self.tree.heading(col_id, text=heading, command=lambda c=col_id: self._sort(c))
            self.tree.column(col_id, width=width, minwidth=60, anchor=tk.W)

        # Alternating row colours
        self.tree.tag_configure("odd",  background="#ffffff")
        self.tree.tag_configure("even", background="#eef2f7")

        self._all_rows: list[dict] = []
        self._sort_col = "name"
        self._sort_asc = True

    # ── Data Loading ─────────────────────────────────────────────────────────

    def load(self):
        self.refresh_btn.config(state=tk.DISABLED, text="Loading…")
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._all_rows = []

        try:
            db = DatabaseManager()
            user = Session.get_user()
            if not user:
                return

            rows = db.query(
                """
                SELECT c.id, c.name, c.gstin, c.city, c.state,
                       c.phone, c.email, c.currency,
                       c.address, c.country, c.website, c.tax_id,
                       c.bank_name, c.account_number, c.ifsc_code,
                       COALESCE(c.is_deleted, 0) AS is_deleted
                FROM user_company uc
                INNER JOIN company c ON uc.company_id = c.id
                WHERE uc.user_id = ?
                ORDER BY c.name ASC
                """,
                [user.id],
            )
            self._all_rows = rows
            self._apply_filter()

        except Exception as exc:
            show_error(
                self.winfo_toplevel(),
                "Failed to Load Companies",
                "An error occurred while loading company data.",
                exc,
            )
        finally:
            self.refresh_btn.config(state=tk.NORMAL, text="↻ Refresh")

    # ── Filtering & Sorting ───────────────────────────────────────────────────

    def _apply_filter(self):
        term = self.search_var.get().strip().lower()
        filtered = (
            self._all_rows
            if not term
            else [
                r for r in self._all_rows
                if term in (r.get("name") or "").lower()
                or term in (r.get("gstin") or "").lower()
                or term in (r.get("city") or "").lower()
                or term in (r.get("state") or "").lower()
                or term in (r.get("email") or "").lower()
            ]
        )

        filtered = sorted(
            filtered,
            key=lambda r: (r.get(self._sort_col) or "").lower(),
            reverse=not self._sort_asc,
        )

        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, row in enumerate(filtered):
            tag = "odd" if idx % 2 == 0 else "even"
            values = [
                row.get("name", ""),
                row.get("gstin", ""),
                row.get("city", ""),
                row.get("state", ""),
                row.get("phone", ""),
                row.get("email", ""),
                row.get("currency", ""),
                "Yes" if row.get("is_deleted") else "No",
            ]
            self.tree.insert("", tk.END, iid=row["id"], values=values, tags=(tag,))

        count = len(filtered)
        total = len(self._all_rows)
        self.count_lbl.config(
            text=f"{count} of {total} companies" if term else f"{total} companies"
        )

    def _sort(self, col: str):
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        self._apply_filter()
