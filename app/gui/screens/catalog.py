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
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.books_by_row = {}

        self._show_all()

    def _show_all(self):
        self.warning_label.config(text="")
        books = self.app.services.catalog.list_books()
        self._populate(books)

    def _search(self):
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

    def _go_home(self):
        from app.gui.screens.home import HomeScreen
        self.app.show_screen(HomeScreen, user=self.user)
