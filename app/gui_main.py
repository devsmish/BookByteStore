from app.bootstrap import build_services
from app.database import (
    DatabaseConnectionError,
    get_edit_connection,
    get_read_connection,
    init_db,
)
from app.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


def main():
    setup_logging()
    logger.info("GUI application starting")

    try:
        init_db()

        with get_read_connection() as read_connection, get_edit_connection() as edit_connection:
            services = build_services(read_connection, edit_connection)

            from app.gui.app import BookstoreApp
            app = BookstoreApp(services)
            app.mainloop()

    except DatabaseConnectionError as e:
        logger.error("Startup failed: %s", e)
        _show_startup_error(f"Database connection error: {e}")
    except Exception:
        logger.exception("Unexpected error")
        _show_startup_error("An unexpected error occurred. Details have been recorded in the log.")
    finally:
        logger.info("GUI application stopped")


def _show_startup_error(message):
    """It displays the error in a window rather than using `print()`—the
    console might not be visible before `mainloop` starts."""
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("BookByteStore — startup error", message)
    root.destroy()


if __name__ == "__main__":
    main()
