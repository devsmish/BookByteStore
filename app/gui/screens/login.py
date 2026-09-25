import tkinter as tk
from tkinter import ttk

from app.exceptions import BookstoreError


class LoginScreen(ttk.Frame):
    def __init__(self, parent, app, message=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app

        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(wrapper, text="BookByteStore", font=("", 20, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 4)
        )

        if message:
            ttk.Label(wrapper, text=message, foreground="green").grid(
                row=1, column=0, columnspan=2, pady=(0, 12)
            )

        ttk.Label(wrapper, text="Username:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=4)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(wrapper, textvariable=self.username_var)
        username_entry.grid(row=2, column=1, pady=4)
        username_entry.bind("<Return>", lambda event: self._login())
        username_entry.focus_set()

        ttk.Label(wrapper, text="Password:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=4)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(wrapper, textvariable=self.password_var, show="*")
        password_entry.grid(row=3, column=1, pady=4)
        password_entry.bind("<Return>", lambda event: self._login())

        self.error_label = ttk.Label(wrapper, text="", foreground="red")
        self.error_label.grid(row=4, column=0, columnspan=2, pady=(8, 8))

        button_row = ttk.Frame(wrapper)
        button_row.grid(row=5, column=0, columnspan=2)
        ttk.Button(button_row, text="Login", command=self._login).pack(side="left", padx=4)
        ttk.Button(button_row, text="Register instead", command=self._go_to_register).pack(side="left", padx=4)

    def _login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        try:
            user = self.app.services.auth.login(username, password)
        except BookstoreError as e:
            self.error_label.config(text=str(e))
            return

        from app.gui.screens.home import HomeScreen
        self.app.show_screen(HomeScreen, user=user)

    def _go_to_register(self):
        from app.gui.screens.register import RegisterScreen
        self.app.show_screen(RegisterScreen)
