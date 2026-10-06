from tkinter import ttk


class HomeScreen(ttk.Frame):
    """The screen that appears after a successful login currently confirms
    the successful login, opens the book catalog, and allows the user to log out."""

    def __init__(self, parent, app, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.user = user

        ttk.Label(self, text=f"Welcome, {user.username}!", font=("", 18, "bold")).pack(pady=(60, 8))

        role = "admin" if user.is_admin else "user"
        ttk.Label(self, text=f"Role: {role}").pack()
        self.balance_label = ttk.Label(self, text=f"Balance: ${user.balance}")
        self.balance_label.pack(pady=(4, 24))

        ttk.Button(self, text="Browse catalog", command=self._go_catalog).pack(pady=(0, 8))
        ttk.Button(self, text="Purchase history", command=self._go_history).pack(pady=(0, 8))
        ttk.Button(self, text="Top up balance", command=self._open_top_up).pack(pady=(0, 8))
        if user.is_admin:
            ttk.Button(self, text="Admin panel", command=self._go_admin).pack(pady=(0, 8))
        ttk.Button(self, text="Log out", command=self._logout).pack()

    def _go_admin(self):
        from app.gui.screens.admin import AdminScreen
        self.app.show_screen(AdminScreen, user=self.user)

    def _go_catalog(self):
        from app.gui.screens.catalog import CatalogScreen
        self.app.show_screen(CatalogScreen, user=self.user)

    def _go_history(self):
        from app.gui.screens.history import HistoryScreen
        self.app.show_screen(HistoryScreen, user=self.user)

    def _open_top_up(self):
        from app.gui.screens.top_up_dialog import TopUpDialog
        TopUpDialog(self, self.app, self.user, on_success=self._on_balance_updated)

    def _on_balance_updated(self, new_balance):
        self.balance_label.config(text=f"Balance: ${new_balance}")

    def _logout(self):
        from app.gui.screens.login import LoginScreen
        self.app.show_screen(LoginScreen)
