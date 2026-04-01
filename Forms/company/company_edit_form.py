"""
Company Edit Form – modal dialog to view and edit an existing company record.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from Services.company_service import CompanyService
from Forms.error_dialog import show_error

BG = "#f4f6f9"


class CompanyEditForm:
    """Modal Toplevel dialog for editing a company.

    Args:
        parent:     Parent Tk window (used for grab_set positioning).
        company_id: UUID of the company to edit.
        on_saved:   Optional callback(company_id) invoked after a successful save.
    """

    def __init__(self, parent: tk.Widget, company_id: str, on_saved=None):
        self._parent = parent
        self._company_id = company_id
        self._on_saved = on_saved

        self._dlg = tk.Toplevel(parent)
        self._dlg.title("Edit Company")
        self._dlg.geometry("680x540")
        self._dlg.resizable(True, True)
        self._dlg.configure(bg=BG)
        self._dlg.grab_set()
        self._dlg.focus_set()

        self._vars: dict[str, tk.StringVar] = {}
        self._build_ui()
        self._load()

    # ── UI Build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self._dlg, bg="#2d4a6e", padx=16, pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(
            hdr, text="Edit Company",
            font=("Segoe UI", 13, "bold"),
            bg="#2d4a6e", fg="#ffffff",
        ).pack(anchor=tk.W)

        # Notebook with tabs
        nb = ttk.Notebook(self._dlg)
        nb.pack(fill=tk.BOTH, expand=True, padx=16, pady=(12, 0))

        # ── Tab 1: General ────────────────────────────────────────────────
        t1 = tk.Frame(nb, bg=BG, padx=16, pady=12)
        nb.add(t1, text="  General  ")
        t1.columnconfigure(1, weight=1)
        t1.columnconfigure(3, weight=1)

        self._field("Company Name *", "name",     t1, 0, col=0)
        self._field("GSTIN",          "gstin",    t1, 1, col=0)
        self._field("Phone",          "phone",    t1, 2, col=0)
        self._field("Email *",        "email",    t1, 3, col=0)
        self._field("Website",        "website",  t1, 4, col=0)
        self._field("Currency",       "currency", t1, 5, col=0)
        self._field("Tax ID",         "tax_id",   t1, 6, col=0)

        # ── Tab 2: Address ────────────────────────────────────────────────
        t2 = tk.Frame(nb, bg=BG, padx=16, pady=12)
        nb.add(t2, text="  Address  ")
        t2.columnconfigure(1, weight=1)
        t2.columnconfigure(3, weight=1)

        self._field("Address",    "address",    t2, 0, col=0)
        self._field("City",       "city",       t2, 1, col=0)
        self._field("State *",    "state",      t2, 2, col=0)
        self._field("State Code", "state_code", t2, 3, col=0)
        self._field("Zip Code",   "zip_code",   t2, 4, col=0)
        self._field("Country *",  "country",    t2, 5, col=0)

        # ── Tab 3: Bank Details ───────────────────────────────────────────
        t3 = tk.Frame(nb, bg=BG, padx=16, pady=12)
        nb.add(t3, text="  Bank Details  ")
        t3.columnconfigure(1, weight=1)
        t3.columnconfigure(3, weight=1)

        self._field("Bank Name",       "bank_name",           t3, 0, col=0)
        self._field("Account Number",  "account_number",      t3, 1, col=0)
        self._field("IFSC Code",       "ifsc_code",           t3, 2, col=0)
        self._field("Account Holder",  "account_holder_name", t3, 3, col=0)
        self._field("Branch Name",     "branch_name",         t3, 4, col=0)
        self._field("Swift Code",      "swift_code",          t3, 5, col=0)

        # ── Footer ────────────────────────────────────────────────────────
        footer = tk.Frame(self._dlg, bg=BG)
        footer.pack(fill=tk.X, padx=16, pady=12)

        ttk.Button(footer, text="Save", command=self._save).pack(
            side=tk.RIGHT, padx=(6, 0)
        )
        ttk.Button(footer, text="Cancel", command=self._dlg.destroy).pack(
            side=tk.RIGHT
        )

        self._dlg.bind("<Escape>", lambda _: self._dlg.destroy())

    def _field(
        self,
        label: str,
        key: str,
        parent_frame: tk.Frame,
        row: int,
        col: int = 0,
        width: int = 32,
    ) -> tk.StringVar:
        """Create a label + entry pair, register the StringVar, return it."""
        tk.Label(
            parent_frame, text=label,
            bg=BG, anchor=tk.W,
            font=("Segoe UI", 9),
        ).grid(row=row, column=col * 2, sticky=tk.W, padx=(0, 8), pady=4)

        var = tk.StringVar()
        self._vars[key] = var
        ttk.Entry(parent_frame, textvariable=var, width=width).grid(
            row=row, column=col * 2 + 1, sticky=tk.EW, padx=(0, 16), pady=4
        )
        return var

    # ── Data Load / Save ──────────────────────────────────────────────────────

    def _load(self):
        data = CompanyService.get_by_id(self._company_id)
        if not data:
            show_error(
                self._parent,
                "Company Not Found",
                f"No company found with id: {self._company_id}",
            )
            self._dlg.destroy()
            return

        for key, var in self._vars.items():
            var.set(data.get(key) or "")

    def _save(self):
        data = {k: v.get().strip() for k, v in self._vars.items()}

        if not data.get("name"):
            messagebox.showwarning(
                "Validation Error", "Company Name is required.", parent=self._dlg
            )
            return

        try:
            CompanyService.update_company(self._company_id, data)
            if self._on_saved:
                self._on_saved(self._company_id)
            self._dlg.destroy()
        except Exception as exc:
            show_error(self._dlg, "Save Failed", "Could not save company changes.", exc)
