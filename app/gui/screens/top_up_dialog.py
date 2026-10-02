import tkinter as tk
from tkinter import ttk

from app.exceptions import BookstoreError
from app.money import parse_money


class TopUpDialog(tk.Toplevel):
    """A modal dialog overlaid on the calling screen. on_success(new_balance)
    is called after a successful top-up — the calling screen itself decides
    how to update its balance display."""

    def __init__(self, parent, app, user, on_success, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.user = user
        self.on_success = on_success

        self.title("Top up balance")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()  # blocks interaction with the parent window while the dialog is open

        wrapper = ttk.Frame(self, padding=16)
        wrapper.pack()

        ttk.Label(wrapper, text="Amount:").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(wrapper, textvariable=self.amount_var)
        amount_entry.grid(row=0, column=1, pady=4)
        amount_entry.bind("<Return>", lambda event: self._submit())
        amount_entry.focus_set()

        self.error_label = ttk.Label(wrapper, text="", foreground="red")
        self.error_label.grid(row=1, column=0, columnspan=2, pady=(4, 8))

        button_row = ttk.Frame(wrapper)
        button_row.grid(row=2, column=0, columnspan=2)
        ttk.Button(button_row, text="Top up", command=self._submit).pack(side="left", padx=4)
        ttk.Button(button_row, text="Cancel", command=self.destroy).pack(side="left", padx=4)

    def _submit(self):
        try:
            amount = parse_money(self.amount_var.get())
        except ValueError:
            self.error_label.config(text="Invalid amount")
            return

        try:
            new_balance = self.app.services.purchase.top_up(self.user.id, amount)
        except BookstoreError as e:
            self.error_label.config(text=str(e))
            return

        self.user.balance = new_balance
        self.on_success(new_balance)
        self.destroy()
