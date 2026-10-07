from tkinter import filedialog, ttk

from app.exceptions import BookstoreError
from app.gui.dialogs import confirm
from app.gui.style import PAD


class AdminScreen(ttk.Frame):
    def __init__(self, parent, app, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.user = user

        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=PAD, pady=(12, 4))
        ttk.Label(top_bar, text="Admin Panel", font=("", 16, "bold")).pack(side="left")
        ttk.Button(top_bar, text="Back", command=self._go_home).pack(side="right")

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", padx=PAD, pady=(0, 8))
        ttk.Button(action_bar, text="Add book", command=self._open_add_dialog).pack(side="left")
        ttk.Button(action_bar, text="Edit selected", command=self._open_edit_dialog).pack(side="left", padx=(6, 0))
        ttk.Button(action_bar, text="Delete selected", command=self._delete_selected).pack(side="left", padx=(6, 0))
        ttk.Button(action_bar, text="Import from file...", command=self._import_from_file).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(action_bar, text="View deleted books", command=self._go_deleted).pack(side="left", padx=(6, 0))

        self.result_label = ttk.Label(self, text="")
        self.result_label.pack(fill="x", padx=PAD)

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
        self.tree.pack(fill="both", expand=True, padx=PAD, pady=(0, 12))

        self.books_by_row = {}
        self._refresh()

    def _refresh(self):
        self.result_label.config(text="")
        books = self.app.services.admin.list_books()
        self.tree.delete(*self.tree.get_children())
        self.books_by_row.clear()
        for book in books:
            row_id = self.tree.insert("", "end", values=(book.title, book.author, f"${book.price}", book.stock))
            self.books_by_row[row_id] = book

    def _selected_book(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return self.books_by_row.get(selection[0])

    def _open_add_dialog(self):
        from app.gui.screens.book_form_dialog import BookFormDialog
        BookFormDialog(self, self.app, on_success=self._refresh)

    def _open_edit_dialog(self):
        book = self._selected_book()
        if not book:
            self.result_label.config(text="Select a book first.", foreground="red")
            return
        from app.gui.screens.book_form_dialog import BookFormDialog
        BookFormDialog(self, self.app, book=book, on_success=self._refresh)

    def _delete_selected(self):
        book = self._selected_book()
        if not book:
            self.result_label.config(text="Select a book first.", foreground="red")
            return

        if not confirm(self, "Delete book", f"Delete '{book.title}'? This can be undone from 'View deleted books'."):
            return

        try:
            self.app.services.admin.delete_book(book.id)
        except BookstoreError as e:
            self.result_label.config(text=str(e), foreground="red")
            return
        self._refresh()
        self.result_label.config(text=f"Deleted '{book.title}'.", foreground="green")

    def _import_from_file(self):
        filename = filedialog.askopenfilename(
            title="Select books file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not filename:
            return

        try:
            added = self.app.services.admin.import_from_file(filename)
        except FileNotFoundError:
            self.result_label.config(text=f"File not found: {filename}", foreground="red")
            return
        except BookstoreError as e:
            self.result_label.config(text=str(e), foreground="red")
            return

        self._refresh()
        self.result_label.config(text=f"{added} new books loaded.", foreground="green")

    def _go_deleted(self):
        from app.gui.screens.deleted_books import DeletedBooksScreen
        self.app.show_screen(DeletedBooksScreen, user=self.user)

    def _go_home(self):
        from app.gui.screens.home import HomeScreen
        self.app.show_screen(HomeScreen, user=self.user)
