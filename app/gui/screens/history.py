from tkinter import ttk


class HistoryScreen(ttk.Frame):
    def __init__(self, parent, app, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.user = user

        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=12, pady=(12, 4))
        ttk.Label(top_bar, text="Purchase History", font=("", 16, "bold")).pack(side="left")
        ttk.Button(top_bar, text="Back", command=self._go_home).pack(side="right")

        self.info_label = ttk.Label(self, text="")
        self.info_label.pack(fill="x", padx=12, anchor="w")

        columns = ("date", "title", "author", "quantity", "price", "total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, heading, width, anchor in (
            ("date", "Date", 100, "w"),
            ("title", "Title", 220, "w"),
            ("author", "Author", 160, "w"),
            ("quantity", "Qty", 60, "center"),
            ("price", "Price", 80, "center"),
            ("total", "Total", 80, "center"),
        ):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._load_history()

    def _load_history(self):
        history = self.app.services.purchase.history(self.user.id)
        self.tree.delete(*self.tree.get_children())

        if not history:
            self.info_label.config(text="No purchases yet.")
            return

        self.info_label.config(text="")
        for p in history:
            self.tree.insert(
                "", "end",
                values=(p.purchase_date, p.title, p.author, p.quantity, f"${p.price}", f"${p.total}"),
            )

    def _go_home(self):
        from app.gui.screens.home import HomeScreen
        self.app.show_screen(HomeScreen, user=self.user)
