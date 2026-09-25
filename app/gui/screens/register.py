import tkinter as tk
from tkinter import ttk

from app.exceptions import BookstoreError
from app.money import parse_money


class RegisterScreen(ttk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app

        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(wrapper, text="BookByteStore — Registration", font=("", 20, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )

        ttk.Label(wrapper, text="Username:").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(wrapper, textvariable=self.username_var)
        username_entry.grid(row=1, column=1, pady=4)
        username_entry.focus_set()

        ttk.Label(wrapper, text="Password:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=4)
        self.password_var = tk.StringVar()
        ttk.Entry(wrapper, textvariable=self.password_var, show="*").grid(row=2, column=1, pady=4)

        ttk.Label(wrapper, text="Starting balance:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=4)
        self.balance_var = tk.StringVar(value="0")
        balance_entry = ttk.Entry(wrapper, textvariable=self.balance_var)
        balance_entry.grid(row=3, column=1, pady=4)
        balance_entry.bind("<Return>", lambda event: self._register())

        self.error_label = ttk.Label(wrapper, text="", foreground="red")
        self.error_label.grid(row=4, column=0, columnspan=2, pady=(8, 8))

        button_row = ttk.Frame(wrapper)
        button_row.grid(row=5, column=0, columnspan=2)
        ttk.Button(button_row, text="Register", command=self._register).pack(side="left", padx=4)
        ttk.Button(button_row, text="Back to login", command=self._go_to_login).pack(side="left", padx=4)

    def _register(self):
        username = self.username_var.get()
        password = self.password_var.get()

        try:
            balance = parse_money(self.balance_var.get())
        except ValueError:
            self.error_label.config(text="Invalid balance")
            return

        try:
            self.app.services.auth.register(username, password, balance)
        except BookstoreError as e:
            self.error_label.config(text=str(e))
            return

        self._go_to_login(message="Registration successful — please log in.")

    def _go_to_login(self, message=None):
        from app.gui.screens.login import LoginScreen
        self.app.show_screen(LoginScreen, message=message)
