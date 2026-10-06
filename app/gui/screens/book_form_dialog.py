import tkinter as tk
from tkinter import ttk

from app.exceptions import BookstoreError
from app.money import parse_money


class BookFormDialog(tk.Toplevel):
    """Modal form for adding/editing a book.
    book=None -> adding, book=<Book> -> editing (fields pre-filled)."""

    def __init__(self, parent, app, on_success, book=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.on_success = on_success
        self.book = book

        self.title("Edit book" if book else "Add book")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        wrapper = ttk.Frame(self, padding=16)
        wrapper.pack()

        ttk.Label(wrapper, text="Title:").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
        self.title_var = tk.StringVar(value=book.title if book else "")
        title_entry = ttk.Entry(wrapper, textvariable=self.title_var, width=30)
        title_entry.grid(row=0, column=1, pady=4)
        title_entry.focus_set()

        ttk.Label(wrapper, text="Author:").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
        self.author_var = tk.StringVar(value=book.author if book else "")
        ttk.Entry(wrapper, textvariable=self.author_var, width=30).grid(row=1, column=1, pady=4)

        ttk.Label(wrapper, text="Price:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=4)
        self.price_var = tk.StringVar(value=str(book.price) if book else "")
        ttk.Entry(wrapper, textvariable=self.price_var, width=30).grid(row=2, column=1, pady=4)

        ttk.Label(wrapper, text="Stock:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=4)
        self.stock_var = tk.StringVar(value=str(book.stock) if book else "")
        stock_entry = ttk.Entry(wrapper, textvariable=self.stock_var, width=30)
        stock_entry.grid(row=3, column=1, pady=4)
        stock_entry.bind("<Return>", lambda event: self._submit())

        self.error_label = ttk.Label(wrapper, text="", foreground="red")
        self.error_label.grid(row=4, column=0, columnspan=2, pady=(4, 8))

        button_row = ttk.Frame(wrapper)
        button_row.grid(row=5, column=0, columnspan=2)
        ttk.Button(button_row, text="Save", command=self._submit).pack(side="left", padx=4)
        ttk.Button(button_row, text="Cancel", command=self.destroy).pack(side="left", padx=4)

    def _submit(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()

        try:
            price = parse_money(self.price_var.get())
            stock = int(self.stock_var.get())
        except ValueError:
            self.error_label.config(text="Invalid price or stock.")
            return

        try:
            if self.book:
                self.app.services.admin.update_book(self.book.id, title, author, price, stock)
            else:
                self.app.services.admin.add_book(title, author, price, stock)
        except BookstoreError as e:
            self.error_label.config(text=str(e))
            return

        self.on_success()
        self.destroy()
