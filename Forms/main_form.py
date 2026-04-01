"""
Main Form – dashboard window shown after successful login.
"""

import tkinter as tk
from tkinter import ttk
from Services.session import Session
from Services.auth_service import AuthService
from Services.async_runner import AsyncRunner
from Services.pull_service import PullService
from Database.db_manager import DatabaseManager
from Database.sync_service import SyncService
from Forms.error_dialog import show_error
from Forms.company.company_list import CompanyListForm


# Sidebar nav items: (label, icon_char, section_key)
NAV_ITEMS = [
    ("Dashboard",       "⊞", "dashboard"),
    ("─────────────", "", None),          # separator
    ("Companies",       "🏢", "companies"),
    ("Transactions",    "⇌", "transactions"),
    ("Ledgers",         "≡", "ledgers"),
    ("Products",        "◫", "products"),
    ("─────────────", "", None),
    ("Reports",         "▤", "reports"),
    ("Settings",        "⚙", "settings"),
]

BG_SIDEBAR   = "#1e2a3a"
FG_SIDEBAR   = "#c8d6e5"
BG_ACTIVE    = "#2d4a6e"
FG_ACTIVE    = "#ffffff"
BG_HEADER    = "#2d4a6e"
FG_HEADER    = "#ffffff"
BG_CONTENT   = "#f4f6f9"


class MainForm:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Accounting ERP – Dashboard")
        self.root.state("zoomed")          # start maximized
        self.root.minsize(900, 600)

        self._active_section = "dashboard"
        self._nav_buttons: dict[str, tk.Label] = {}
        self._content_frames: dict[str, ttk.Frame] = {}
        self._company = Session.get_selected_company()

        self._build_header()
        self._build_body()
        self._build_status_bar()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Auto-pull selected company data from cloud
        if self._company:
            self.root.after(300, self._pull_company_data)

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_HEADER, height=48)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(
            header, text="  Accounting ERP",
            font=("Segoe UI", 13, "bold"),
            bg=BG_HEADER, fg=FG_HEADER,
        ).pack(side=tk.LEFT, padx=(8, 0))

        # Selected company name
        company_name = self._company.get("name", "") if self._company else ""
        if company_name:
            tk.Label(
                header, text="  |  ",
                font=("Segoe UI", 11),
                bg=BG_HEADER, fg="#7fb3d8",
            ).pack(side=tk.LEFT)
            self.company_lbl = tk.Label(
                header, text=company_name,
                font=("Segoe UI", 11, "bold"),
                bg=BG_HEADER, fg="#f1c40f",
            )
            self.company_lbl.pack(side=tk.LEFT)

        # User info + logout on the right
        user = Session.get_user()
        user_label = user.display_name if user else ""

        logout_btn = tk.Label(
            header, text="  Logout  ",
            font=("Segoe UI", 9),
            bg="#c0392b", fg=FG_HEADER,
            cursor="hand2", padx=4, pady=2,
        )
        logout_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        logout_btn.bind("<Button-1>", lambda _e: self._logout())

        # Pull from Cloud button
        self.push_btn = tk.Label(
            header, text="  ↑ Push to Cloud  ",
            font=("Segoe UI", 9),
            bg="#e67e22", fg=FG_HEADER,
            cursor="hand2", padx=6, pady=2,
        )
        self.push_btn.pack(side=tk.RIGHT, padx=(0, 6), pady=10)
        self.push_btn.bind("<Button-1>", lambda _e: self._on_push())

        self.pull_btn = tk.Label(
            header, text="  ↓ Pull from Cloud  ",
            font=("Segoe UI", 9),
            bg="#27ae60", fg=FG_HEADER,
            cursor="hand2", padx=6, pady=2,
        )
        self.pull_btn.pack(side=tk.RIGHT, padx=(0, 6), pady=10)
        self.pull_btn.bind("<Button-1>", lambda _e: self._on_pull())

        tk.Label(
            header, text=f"👤  {user_label}",
            font=("Segoe UI", 9),
            bg=BG_HEADER, fg=FG_HEADER,
        ).pack(side=tk.RIGHT, padx=(0, 8))

    # ── Body (sidebar + content) ──────────────────────────────────────────────

    def _build_body(self):
        body = tk.Frame(self.root)
        body.pack(fill=tk.BOTH, expand=True)

        # ── Sidebar ───────────────────
        sidebar = tk.Frame(body, bg=BG_SIDEBAR, width=200)
        sidebar.pack(fill=tk.Y, side=tk.LEFT)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="MENU",
            font=("Segoe UI", 8, "bold"),
            bg=BG_SIDEBAR, fg="#7f8c9a",
        ).pack(anchor=tk.W, padx=16, pady=(16, 8))

        for label, icon, key in NAV_ITEMS:
            if key is None:
                tk.Label(sidebar, text="", bg=BG_SIDEBAR, height=1).pack(fill=tk.X)
                continue
            self._add_nav_item(sidebar, icon, label, key)

        # ── Content area ──────────────
        self.content_area = tk.Frame(body, bg=BG_CONTENT)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        self._build_sections()
        self._show_section("dashboard")

    def _add_nav_item(self, parent, icon, label, key):
        frame = tk.Frame(parent, bg=BG_SIDEBAR, cursor="hand2")
        frame.pack(fill=tk.X)

        lbl = tk.Label(
            frame,
            text=f"  {icon}  {label}",
            font=("Segoe UI", 10),
            bg=BG_SIDEBAR, fg=FG_SIDEBAR,
            anchor=tk.W, padx=8, pady=9,
        )
        lbl.pack(fill=tk.X)

        self._nav_buttons[key] = lbl

        for widget in (frame, lbl):
            widget.bind("<Button-1>", lambda _e, k=key: self._show_section(k))
            widget.bind("<Enter>",    lambda _e, w=lbl, k=key: self._nav_hover(w, k, True))
            widget.bind("<Leave>",    lambda _e, w=lbl, k=key: self._nav_hover(w, k, False))

    def _nav_hover(self, label: tk.Label, key: str, entering: bool):
        if key == self._active_section:
            return
        label.config(bg=BG_ACTIVE if entering else BG_SIDEBAR)

    # ── Sections ─────────────────────────────────────────────────────────────

    def _build_sections(self):
        self._content_frames["dashboard"]    = self._make_dashboard()
        self._content_frames["companies"]    = CompanyListForm(self.content_area)
        self._content_frames["transactions"] = self._make_placeholder("Transactions")
        self._content_frames["ledgers"]      = self._make_placeholder("Ledgers")
        self._content_frames["products"]     = self._make_placeholder("Products")
        self._content_frames["reports"]      = self._make_placeholder("Reports")
        self._content_frames["settings"]     = self._make_placeholder("Settings")

    def _show_section(self, key: str):
        # Update nav highlight
        if self._active_section in self._nav_buttons:
            self._nav_buttons[self._active_section].config(bg=BG_SIDEBAR, fg=FG_SIDEBAR)
        self._active_section = key
        if key in self._nav_buttons:
            self._nav_buttons[key].config(bg=BG_ACTIVE, fg=FG_ACTIVE)

        # Swap content frame
        for frame in self._content_frames.values():
            frame.pack_forget()
        self._content_frames[key].pack(fill=tk.BOTH, expand=True)

    # ── Dashboard section ─────────────────────────────────────────────────────

    def _make_dashboard(self) -> tk.Frame:
        frame = tk.Frame(self.content_area, bg=BG_CONTENT)

        ttk.Label(
            frame, text="Dashboard",
            font=("Segoe UI", 16, "bold"),
            background=BG_CONTENT,
        ).pack(anchor=tk.W, padx=24, pady=(24, 4))

        ttk.Separator(frame).pack(fill=tk.X, padx=24)

        user = Session.get_user()
        greeting = f"Welcome back, {user.display_name}!" if user else "Welcome!"
        ttk.Label(
            frame, text=greeting,
            font=("Segoe UI", 11),
            background=BG_CONTENT,
        ).pack(anchor=tk.W, padx=24, pady=(16, 0))

        # ── Companies section ─────────
        ttk.Label(
            frame, text="Your Companies",
            font=("Segoe UI", 13, "bold"),
            background=BG_CONTENT,
        ).pack(anchor=tk.W, padx=24, pady=(24, 8))

        self.companies_frame = tk.Frame(frame, bg=BG_CONTENT)
        self.companies_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))

        self._load_companies()

        return frame

    def _load_companies(self):
        """Load user companies from local SQLite and display as cards."""
        for w in self.companies_frame.winfo_children():
            w.destroy()

        db = DatabaseManager()
        user = Session.get_user()
        if not user:
            return

        user_companies = db.query(
            'SELECT uc.company_id, c.name, c.city, c.state, c.gstin, c.email '
            'FROM user_company uc '
            'INNER JOIN company c ON uc.company_id = c.id '
            'WHERE uc.user_id = ?',
            [user.id],
        )

        if not user_companies:
            ttk.Label(
                self.companies_frame,
                text='No companies found. Click "↓ Pull from Cloud" to sync your data.',
                font=("Segoe UI", 10),
                background=BG_CONTENT, foreground="#888",
            ).pack(anchor=tk.W, pady=8)
            return

        for idx, company in enumerate(user_companies):
            card = tk.Frame(
                self.companies_frame, bg="#ffffff",
                highlightbackground="#dce1e8", highlightthickness=1,
                padx=16, pady=12,
            )
            card.pack(fill=tk.X, pady=(0, 8))

            tk.Label(
                card, text=company.get("name", ""),
                font=("Segoe UI", 12, "bold"),
                bg="#ffffff", fg="#2c3e50", anchor=tk.W,
            ).pack(fill=tk.X)

            detail_parts = []
            if company.get("city"):
                detail_parts.append(company["city"])
            if company.get("state"):
                detail_parts.append(company["state"])
            if company.get("gstin"):
                detail_parts.append(f"GSTIN: {company['gstin']}")

            if detail_parts:
                tk.Label(
                    card, text="  |  ".join(detail_parts),
                    font=("Segoe UI", 9),
                    bg="#ffffff", fg="#7f8c8d", anchor=tk.W,
                ).pack(fill=tk.X, pady=(2, 0))

            if company.get("email"):
                tk.Label(
                    card, text=company["email"],
                    font=("Segoe UI", 9),
                    bg="#ffffff", fg="#3498db", anchor=tk.W,
                ).pack(fill=tk.X, pady=(2, 0))

    def _make_placeholder(self, title: str) -> tk.Frame:
        frame = tk.Frame(self.content_area, bg=BG_CONTENT)
        ttk.Label(
            frame, text=title,
            font=("Segoe UI", 16, "bold"),
            background=BG_CONTENT,
        ).pack(anchor=tk.W, padx=24, pady=(24, 4))
        ttk.Separator(frame).pack(fill=tk.X, padx=24)
        ttk.Label(
            frame, text=f"{title} forms will appear here.",
            font=("Segoe UI", 10),
            background=BG_CONTENT,
        ).pack(anchor=tk.W, padx=24, pady=16)
        return frame

    # ── Pull selected company data ─────────────────────────────────────────

    def _pull_company_data(self):
        if not self._company:
            return
        company_id = self._company["id"]
        self.pull_btn.config(text="  Syncing…  ", bg="#7f8c8d")
        self.status_var.set(f"Pulling data for {self._company.get('name', '')}…")

        def _callback(result, exc):
            if exc:
                self.root.after(0, self._pull_done, False, str(exc))
            else:
                success, message = result
                self.root.after(0, self._pull_done, success, message)

        AsyncRunner.run(
            PullService.pull_company(company_id, progress_callback=self._pull_progress),
            callback=_callback,
        )

    # ── Pull from Cloud ─────────────────────────────────────────────────────

    def _on_pull(self):
        self.pull_btn.config(text="  Syncing…  ", bg="#7f8c8d")
        self.status_var.set("Pulling data from cloud…")

        def _callback(result, exc):
            if exc:
                self.root.after(0, self._pull_done, False, str(exc))
            else:
                success, message = result
                self.root.after(0, self._pull_done, success, message)

        AsyncRunner.run(PullService.pull_all(progress_callback=self._pull_progress), callback=_callback)

    def _pull_progress(self, message: str):
        self.root.after(0, lambda: self.status_var.set(message))

    def _pull_done(self, success: bool, message: str):
        self.pull_btn.config(text="  ↓ Pull from Cloud  ", bg="#27ae60")
        self.status_var.set(message)
        if success:
            self._load_companies()
            companies_frame = self._content_frames.get("companies")
            if companies_frame:
                companies_frame.load()
        else:
            show_error(self.root, "Pull Failed", message)

    # ── Push to Cloud ─────────────────────────────────────────────────────────

    def _on_push(self):
        self.push_btn.config(text="  Pushing…  ", bg="#7f8c8d")
        self.status_var.set("Pushing changes to cloud…")

        def _callback(result, exc):
            if exc:
                self.root.after(0, self._push_done, False, str(exc))
            else:
                success, message = result
                self.root.after(0, self._push_done, success, message)

        AsyncRunner.run(
            SyncService.push_to_cloud(progress_callback=self._push_progress),
            callback=_callback,
        )

    def _push_progress(self, message: str):
        self.root.after(0, lambda: self.status_var.set(message))

    def _push_done(self, success: bool, message: str):
        self.push_btn.config(text="  ↑ Push to Cloud  ", bg="#e67e22")
        self.status_var.set(message)
        if not success:
            show_error(self.root, "Push Failed", message)

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            self.root, textvariable=self.status_var,
            relief=tk.SUNKEN, anchor=tk.W,
            bg="#dde3ec", fg="#555",
            font=("Segoe UI", 8),
        ).pack(side=tk.BOTTOM, fill=tk.X)

    # ── Logout ────────────────────────────────────────────────────────────────

    def _logout(self):
        AuthService.logout()
        self.root.destroy()
        from Forms.auth.login_form import LoginForm
        from main import _launch_app
        LoginForm(on_success=_launch_app).run()

    def _on_close(self):
        from Services.async_runner import AsyncRunner
        AsyncRunner.stop()
        self.root.destroy()

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()
