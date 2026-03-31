"""
Copyable error dialog for development – shows full traceback and lets the
user copy it to clipboard.
"""

import tkinter as tk
from tkinter import ttk
import traceback


def show_error(parent, title: str, message: str, exc: Exception = None):
    """Display a modal error dialog with a copyable text area.

    Args:
        parent:  Parent Tk window.
        title:   Dialog title.
        message: Short error summary shown at top.
        exc:     Optional exception – its traceback is appended to the detail area.
    """
    detail = message
    if exc:
        detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        if message and message not in detail:
            detail = message + "\n\n" + detail

    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.resizable(True, True)
    dlg.grab_set()
    dlg.minsize(520, 320)

    # ── Header ────────────────────────────────────────────────────────────
    hdr = tk.Frame(dlg, bg="#c0392b", padx=12, pady=10)
    hdr.pack(fill=tk.X)
    tk.Label(
        hdr, text=f"⚠  {title}",
        font=("Segoe UI", 11, "bold"),
        bg="#c0392b", fg="#ffffff",
    ).pack(anchor=tk.W)

    # ── Detail text (copyable) ────────────────────────────────────────────
    body = tk.Frame(dlg, bg="#fdfdfd", padx=12, pady=8)
    body.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        body,
        text="Error detail (select all → Ctrl+C to copy):",
        font=("Segoe UI", 8),
        bg="#fdfdfd", fg="#555", anchor=tk.W,
    ).pack(anchor=tk.W, pady=(0, 4))

    txt = tk.Text(
        body,
        font=("Consolas", 9),
        bg="#1e1e1e", fg="#f8f8f2",
        insertbackground="#ffffff",
        relief=tk.FLAT,
        wrap=tk.WORD,
        padx=8, pady=6,
    )
    txt.pack(fill=tk.BOTH, expand=True)
    sb = ttk.Scrollbar(body, orient=tk.VERTICAL, command=txt.yview)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    txt.configure(yscrollcommand=sb.set)
    txt.insert("1.0", detail)
    txt.config(state=tk.DISABLED)

    # ── Buttons ───────────────────────────────────────────────────────────
    btn_bar = tk.Frame(dlg, bg="#f0f0f0", padx=12, pady=8)
    btn_bar.pack(fill=tk.X)

    def _copy():
        dlg.clipboard_clear()
        dlg.clipboard_append(detail)
        copy_btn.config(text="Copied!")
        dlg.after(1500, lambda: copy_btn.config(text="Copy to Clipboard"))

    copy_btn = ttk.Button(btn_bar, text="Copy to Clipboard", command=_copy)
    copy_btn.pack(side=tk.LEFT)

    ttk.Button(btn_bar, text="Close", command=dlg.destroy).pack(side=tk.RIGHT)

    # Auto-select all text for quick Ctrl+C
    txt.config(state=tk.NORMAL)
    txt.tag_add(tk.SEL, "1.0", tk.END)
    txt.config(state=tk.DISABLED)

    dlg.transient(parent)
    dlg.focus_set()
    parent.wait_window(dlg)
