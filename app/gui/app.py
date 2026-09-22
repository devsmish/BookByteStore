import tkinter as tk
from tkinter import ttk


class BookstoreApp(tk.Tk):
    """Root window + screen switching controller.

    A single root and a single container; screens are `ttk.Frame` instances
    that are recreated upon each navigation and brought to the foreground
    using `tkraise()`. This allows a screen to receive fresh data via its
    constructor rather than through a separate `update()` method on an
    existing widget.
    """

    def __init__(self, services):
        super().__init__()
        self.services = services

        self.title("BookByteStore")
        self.geometry("800x600")
        self.minsize(600, 400)

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self._container = container
        self._current_screen = None

        from app.gui.screens.placeholder import PlaceholderScreen
        self.show_screen(PlaceholderScreen)

    def show_screen(self, screen_class, **kwargs):
        """Creates a screen of the specified class and makes it visible, destroying the previous one."""
        frame = screen_class(self._container, app=self, **kwargs)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

        old_screen = self._current_screen
        self._current_screen = frame
        if old_screen is not None:
            old_screen.destroy()
