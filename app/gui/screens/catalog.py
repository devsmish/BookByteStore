import tkinter as tk
from tkinter import ttk

from app.exceptions import BookstoreError


class CatalogScreen(ttk.Frame):
    """Browsing the catalog and searching."""

    def __init__(self, parent, app, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.user = user

        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=12, pady=(12, 4))
        ttk.Label(top_bar, text="Catalog", font=("", 16, "bold")).pack(side="left")
        ttk.Button(top_bar, text="Back", command=self._go_home).pack(side="right")
        self.balance_label = ttk.Label(top_bar, text=f"Balance: ${user.balance}")
        self.balance_label.pack(side="right", padx=(0, 12))

        search_bar = ttk.Frame(self)
        search_bar.pack(fill="x", padx=12, pady=(0, 8))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_bar, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<Return>", lambda event: self._search())
        ttk.Button(search_bar, text="Search", command=self._search).pack(side="left", padx=(6, 0))
        ttk.Button(search_bar, text="Show all", command=self._show_all).pack(side="left", padx=(6, 0))

        self.warning_label = ttk.Label(self, text="", foreground="#a06400")
        self.warning_label.pack(fill="x", padx=12)

        columns = ("title", "author", "price", "stock")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, heading, width, anchor in (
            ("title", "Title", 260, "w"),
            ("author", "Author", 180, "w"),
            ("price", "Price", 80, "center"),
            ("stock", "Stock", 80, "center"),
        ):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        purchase_bar = ttk.Frame(self)
        purchase_bar.pack(fill="x", padx=12, pady=(0, 4))
        ttk.Label(purchase_bar, text="Quantity:").pack(side="left")
        self.quantity_var = tk.StringVar(value="1")
        ttk.Entry(purchase_bar, textvariable=self.quantity_var, width=6).pack(side="left", padx=(4, 12))
        ttk.Button(purchase_bar, text="Buy selected", command=self._buy).pack(side="left")

        self.purchase_result_label = ttk.Label(self, text="")
        self.purchase_result_label.pack(fill="x", padx=12, pady=(0, 12))

        self.books_by_row = {}

        self._show_all()

    def _show_all(self):
        self.warning_label.config(text="")
        self.purchase_result_label.config(text="")
        books = self.app.services.catalog.list_books()
        self._populate(books)

    def _search(self):
        self.purchase_result_label.config(text="")
        query = self.search_var.get()
        try:
            books, warning = self.app.services.catalog.search(query)
        except BookstoreError as e:
            self.warning_label.config(text=str(e))
            self._populate([])
            return

        self.warning_label.config(text=warning or "")
        self._populate(books)

    def _populate(self, books):
        self.tree.delete(*self.tree.get_children())
        self.books_by_row.clear()
        for book in books:
            row_id = self.tree.insert("", "end", values=(book.title, book.author, f"${book.price}", book.stock))
            self.books_by_row[row_id] = book

    def _buy(self):
        selection = self.tree.selection()
        if not selection:
            self.purchase_result_label.config(text="Select a book first.", foreground="red")
            return

        book = self.books_by_row.get(selection[0])
        if not book:
            return

        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            self.purchase_result_label.config(text="Quantity must be a positive whole number.", foreground="red")
            return

        try:
            total = self.app.services.purchase.purchase(self.user.id, book.id, quantity)
        except BookstoreError as e:
            self.purchase_result_label.config(text=str(e), foreground="red")
            return

        self.user.balance -= total
        self.balance_label.config(text=f"Balance: ${self.user.balance}")
        self._show_all()
        self.purchase_result_label.config(
            text=f"Bought {quantity} x '{book.title}' for ${total}.", foreground="green"
        )

    def _go_home(self):
        from app.gui.screens.home import HomeScreen
        self.app.show_screen(HomeScreen, user=self.user)
