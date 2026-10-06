from tkinter import ttk

from app.exceptions import BookstoreError


class DeletedBooksScreen(ttk.Frame):
    def __init__(self, parent, app, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.user = user

        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=12, pady=(12, 4))
        ttk.Label(top_bar, text="Deleted Books", font=("", 16, "bold")).pack(side="left")
        ttk.Button(top_bar, text="Back", command=self._go_admin).pack(side="right")

        ttk.Button(self, text="Restore selected", command=self._restore_selected).pack(
            anchor="w", padx=12, pady=(0, 4)
        )

        self.result_label = ttk.Label(self, text="")
        self.result_label.pack(fill="x", padx=12)

        columns = ("title", "author", "deleted_at")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, heading, width, anchor in (
            ("title", "Title", 260, "w"),
            ("author", "Author", 180, "w"),
            ("deleted_at", "Deleted at", 160, "center"),
        ):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.books_by_row = {}
        self._refresh()

    def _refresh(self):
        self.result_label.config(text="")
        books = self.app.services.admin.list_deleted_books()
        self.tree.delete(*self.tree.get_children())
        self.books_by_row.clear()
        for book in books:
            row_id = self.tree.insert("", "end", values=(book.title, book.author, book.deleted_at))
            self.books_by_row[row_id] = book

        if not books:
            self.result_label.config(text="No deleted books.")

    def _restore_selected(self):
        selection = self.tree.selection()
        if not selection:
            self.result_label.config(text="Select a book first.", foreground="red")
            return

        book = self.books_by_row.get(selection[0])
        try:
            self.app.services.admin.restore_book(book.id)
        except BookstoreError as e:
            self.result_label.config(text=str(e), foreground="red")
            return

        self._refresh()
        self.result_label.config(text=f"Restored '{book.title}'.", foreground="green")

    def _go_admin(self):
        from gui.screens.admin import AdminScreen
        self.app.show_screen(AdminScreen, user=self.user)
