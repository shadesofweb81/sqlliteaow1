"""
Select Company Form – lets the user pick which company to work with.
After selection the company's data is pulled from the cloud.
"""

import tkinter as tk
from tkinter import ttk
from Database.db_manager import DatabaseManager
from Services.session import Session
from Forms.error_dialog import show_error

BG = "#f4f6f9"
CARD_BG = "#ffffff"
CARD_HOVER = "#e8f0fe"
CARD_SELECTED = "#d4e6fc"
ACCENT = "#2d4a6e"


class SelectCompanyForm:
    """Modal-style window that lists the user's companies for selection."""

    def __init__(self, on_select=None):
        """
        Args:
            on_select: callback(company_dict) called when user picks a company.
        """
        self._on_select = on_select
        self._companies: list[dict] = []
        self._selected_id: str | None = None
        self._cards: dict[str, tk.Frame] = {}

        self.root = tk.Tk()
        self.root.title("Select Company")
        self.root.geometry("520x460")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._load_companies()

    def _build_ui(self):
        # ── Title ──────────────────────
        tk.Label(
            self.root, text="Select a Company",
            font=("Segoe UI", 16, "bold"),
            bg=BG, fg="#2c3e50",
        ).pack(anchor=tk.W, padx=24, pady=(24, 4))

        tk.Label(
            self.root, text="Choose the company you want to work with:",
            font=("Segoe UI", 10),
            bg=BG, fg="#7f8c8d",
        ).pack(anchor=tk.W, padx=24, pady=(0, 12))

        ttk.Separator(self.root).pack(fill=tk.X, padx=24)

        # ── Scrollable company list ───
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=24, pady=(12, 0))

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        self._list_frame = tk.Frame(canvas, bg=BG)

        self._list_frame.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self._list_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mouse-wheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Bottom buttons ────────────
        btn_bar = tk.Frame(self.root, bg=BG)
        btn_bar.pack(fill=tk.X, padx=24, pady=(8, 16))

        self.select_btn = tk.Label(
            btn_bar, text="  Continue  ",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT, fg="#ffffff",
            cursor="hand2", padx=16, pady=6,
        )
        self.select_btn.pack(side=tk.RIGHT)
        self.select_btn.bind("<Button-1>", lambda _e: self._on_confirm())

    def _load_companies(self):
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._cards.clear()

        try:
            db = DatabaseManager()
            user = Session.get_user()
            if not user:
                return

            self._companies = db.query(
                'SELECT c.id, c.name, c.city, c.state, c.gstin, c.email '
                'FROM user_company uc '
                'INNER JOIN company c ON uc.company_id = c.id '
                'WHERE uc.user_id = ?',
                [user.id],
            )
        except Exception as exc:
            show_error(self.root, "Load Error", "Failed to load companies.", exc)
            return

        if not self._companies:
            tk.Label(
                self._list_frame,
                text='No companies found.\nPlease pull from cloud first.',
                font=("Segoe UI", 10),
                bg=BG, fg="#888", justify=tk.LEFT,
            ).pack(anchor=tk.W, pady=16)
            return

        # Auto-select if only one company
        if len(self._companies) == 1:
            self._selected_id = self._companies[0]["id"]

        for company in self._companies:
            self._add_card(company)

        # Highlight auto-selected
        if self._selected_id:
            self._highlight(self._selected_id)

    def _add_card(self, company: dict):
        cid = company["id"]

        card = tk.Frame(
            self._list_frame, bg=CARD_BG,
            highlightbackground="#dce1e8", highlightthickness=1,
            padx=14, pady=10, cursor="hand2",
        )
        card.pack(fill=tk.X, pady=(0, 6))

        name_lbl = tk.Label(
            card, text=company.get("name", ""),
            font=("Segoe UI", 11, "bold"),
            bg=CARD_BG, fg="#2c3e50", anchor=tk.W,
        )
        name_lbl.pack(fill=tk.X)

        detail_parts = []
        if company.get("city"):
            detail_parts.append(company["city"])
        if company.get("state"):
            detail_parts.append(company["state"])
        if company.get("gstin"):
            detail_parts.append(f"GSTIN: {company['gstin']}")

        detail_lbl = None
        if detail_parts:
            detail_lbl = tk.Label(
                card, text="  |  ".join(detail_parts),
                font=("Segoe UI", 9),
                bg=CARD_BG, fg="#7f8c8d", anchor=tk.W,
            )
            detail_lbl.pack(fill=tk.X, pady=(2, 0))

        self._cards[cid] = card

        # Click binding
        widgets = [card, name_lbl]
        if detail_lbl:
            widgets.append(detail_lbl)
        for w in widgets:
            w.bind("<Button-1>", lambda _e, _id=cid: self._on_card_click(_id))
            w.bind("<Enter>", lambda _e, _id=cid: self._hover(_id, True))
            w.bind("<Leave>", lambda _e, _id=cid: self._hover(_id, False))

    def _on_card_click(self, cid: str):
        self._selected_id = cid
        self._highlight(cid)

    def _highlight(self, cid: str):
        for _cid, card in self._cards.items():
            bg = CARD_SELECTED if _cid == cid else CARD_BG
            card.config(bg=bg)
            for child in card.winfo_children():
                child.config(bg=bg)

    def _hover(self, cid: str, entering: bool):
        if cid == self._selected_id:
            return
        bg = CARD_HOVER if entering else CARD_BG
        card = self._cards[cid]
        card.config(bg=bg)
        for child in card.winfo_children():
            child.config(bg=bg)

    def _on_confirm(self):
        if not self._selected_id:
            return

        company = next(
            (c for c in self._companies if c["id"] == self._selected_id), None
        )
        if not company:
            return

        Session.set_selected_company(company)
        self.root.destroy()

        if self._on_select:
            self._on_select(company)

    def _on_close(self):
        from Services.async_runner import AsyncRunner
        AsyncRunner.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
