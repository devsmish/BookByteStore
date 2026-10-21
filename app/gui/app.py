import tkinter as tk
from tkinter import messagebox, ttk

from app.logging_config import get_logger

logger = get_logger(__name__)


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

        from app.gui.style import apply_style

        apply_style(self)

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self._container = container
        self._current_screen = None

        from app.gui.screens.login import LoginScreen

        self.show_screen(LoginScreen)

    def report_callback_exception(self, exc, val, tb):
        """Tk calls this when ANY button/key/`after` callback raises.

        By default Tk only prints the traceback to stderr, which nobody sees in a windowed app: the
        button just seems dead, and nothing reaches the log file. Log it and tell the user instead.
        """
        logger.error("Unhandled error in a GUI callback: %s", val, exc_info=(exc, val, tb))
        try:
            messagebox.showerror(
                "Unexpected error",
                f"Something went wrong and the action was not completed.\n\n{val}\n\n"
                "Details were written to the log file.",
                parent=self,
            )
        except Exception:
            logger.exception("Could not show the error dialog")

    def show_screen(self, screen_class, **kwargs):
        """Creates a screen of the specified class and makes it visible, destroying the previous one."""
        frame = screen_class(self._container, app=self, **kwargs)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

        old_screen = self._current_screen
        self._current_screen = frame
        if old_screen is not None:
            old_screen.destroy()
