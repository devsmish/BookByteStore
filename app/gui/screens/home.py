from tkinter import ttk


class HomeScreen(ttk.Frame):
    """The screen following a successful login currently confirms
    that the login worked and allows the user to log out."""

    def __init__(self, parent, app, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.user = user

        ttk.Label(self, text=f"Welcome, {user.username}!", font=("", 18, "bold")).pack(pady=(60, 8))

        role = "admin" if user.is_admin else "user"
        ttk.Label(self, text=f"Role: {role}").pack()
        ttk.Label(self, text=f"Balance: ${user.balance}").pack(pady=(4, 24))

        ttk.Label(
            self, text="Catalog, purchases, and admin panel are coming in the next steps."
        ).pack(pady=(0, 24))

        ttk.Button(self, text="Log out", command=self._logout).pack()

    def _logout(self):
        from app.gui.screens.login import LoginScreen
        self.app.show_screen(LoginScreen)
