"""
Login form – first window shown when no session is found.
"""

import tkinter as tk
from tkinter import ttk
from Services.auth_service import AuthService
from Services.async_runner import AsyncRunner


class LoginForm:
    def __init__(self, on_success=None):
        """
        Args:
            on_success: Callable invoked on the main thread after successful login.
        """
        self.on_success = on_success

        self.root = tk.Tk()
        self.root.title("Accounting ERP – Login")
        self.root.resizable(False, False)
        self._build_ui()
        self._center_window(380, 340)

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ────────────────────
        header = ttk.Frame(self.root, padding=(0, 20, 0, 10))
        header.pack(fill=tk.X)
        ttk.Label(
            header, text="Accounting ERP", font=("Segoe UI", 18, "bold")
        ).pack()
        ttk.Label(
            header, text="Sign in to your account", font=("Segoe UI", 10)
        ).pack(pady=(4, 0))

        ttk.Separator(self.root).pack(fill=tk.X, padx=20)

        # ── Form ──────────────────────
        form = ttk.Frame(self.root, padding=(30, 16, 30, 0))
        form.pack(fill=tk.X)
        form.columnconfigure(0, weight=1)

        ttk.Label(form, text="Email / Username").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2)
        )
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(form, textvariable=self.email_var)
        self.email_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))

        ttk.Label(form, text="Password").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 2)
        )
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form, textvariable=self.password_var, show="•")
        self.password_entry.grid(row=3, column=0, sticky=tk.EW, pady=(0, 20))

        # ── Login button ──────────────
        self.login_btn = ttk.Button(
            form, text="Login", command=self._on_login
        )
        self.login_btn.grid(row=4, column=0, sticky=tk.EW)

        # ── Status label ──────────────
        self.status_var = tk.StringVar()
        status = ttk.Label(
            self.root,
            textvariable=self.status_var,
            foreground="red",
            wraplength=320,
            justify=tk.CENTER,
        )
        status.pack(pady=(10, 16))

        # Bind Enter key
        self.root.bind("<Return>", lambda _e: self._on_login())
        self.email_entry.focus_set()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _center_window(self, w, h):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _set_loading(self, loading: bool):
        if loading:
            self.login_btn.config(state=tk.DISABLED, text="Signing in…")
            self.status_var.set("")
        else:
            self.login_btn.config(state=tk.NORMAL, text="Login")

    # ── Login flow ────────────────────────────────────────────────────────────

    def _on_login(self):
        email = self.email_var.get().strip()
        password = self.password_var.get()

        if not email or not password:
            self.status_var.set("Please enter your email and password.")
            return

        self._set_loading(True)

        def _callback(result, exc):
            if exc:
                self.root.after(0, self._handle_result, False, str(exc))
            else:
                success, message, _response = result
                self.root.after(0, self._handle_result, success, message)

        AsyncRunner.run(AuthService.login(email, password), callback=_callback)

    def _handle_result(self, success: bool, message: str):
        self._set_loading(False)
        if success:
            self.root.destroy()
            if self.on_success:
                self.on_success()
        else:
            self.status_var.set(message)

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()
