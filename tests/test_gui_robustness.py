"""An exception inside a Tk callback must not vanish: it is logged and shown to the user.

Needs Tk and a display; skipped automatically when either is missing (e.g. a headless CI runner).
"""
import logging
from types import SimpleNamespace

import pytest


@pytest.fixture
def gui():
    tk = pytest.importorskip("tkinter")
    try:
        probe = tk.Tk()
        probe.destroy()
    except tk.TclError:
        pytest.skip("no display available for Tk")

    from app.gui import app as gui_module

    window = gui_module.BookstoreApp(SimpleNamespace(auth=None, catalog=None, purchase=None, admin=None))
    yield gui_module, window
    window.destroy()


def test_unhandled_callback_error_is_shown_and_logged(gui, monkeypatch, caplog):
    gui_module, window = gui
    shown = []
    monkeypatch.setattr(gui_module.messagebox, "showerror", lambda title, message, **kw: shown.append((title, message)))

    def failing_callback():
        raise RuntimeError("database exploded")

    window.after(0, failing_callback)
    with caplog.at_level(logging.ERROR, logger="bookstore"):
        window.update()

    assert shown, "the user must be told that something went wrong"
    assert "database exploded" in shown[0][1]
    assert any("database exploded" in r.getMessage() for r in caplog.records)
