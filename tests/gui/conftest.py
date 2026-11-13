"""Fixtures for GUI tests.

The screens run against the *real* services built on the in-memory fake repositories from
tests/conftest.py, so a test exercises screen + service logic and the exact messages a user sees,
without a database. Needs Tk and a display; the whole package is skipped when either is missing
(run it on Linux with `xvfb-run -a pytest tests/gui`).

Tk's blocking helpers (messagebox / filedialog) are replaced: a real one would freeze the test.
"""
import dataclasses
from decimal import Decimal

import pytest

from app.bootstrap import Services
from app.services.admin_service import AdminService
from app.services.auth import AuthService
from app.services.catalog_service import CatalogService
from app.services.purchase_service import PurchaseService
from tests.conftest import (
    FakeBookRepo,
    FakeConnection,
    FakePurchaseRepo,
    FakeSearchLogRepo,
    FakeUserRepo,
)
from tests.gui.helpers import click, open_dialogs


class GuiUserRepo(FakeUserRepo):
    """The real repository returns a *fresh* User per login; the plain fake returns the stored object.
    With the shared object, a purchase would be subtracted twice (by the fake repo and by the screen)."""

    def authenticate(self, username, password):
        user = super().authenticate(username, password)
        return dataclasses.replace(user) if user else None


class Dialogs:
    """Stand-ins for the blocking Tk dialogs. Set the answer, then read what was asked."""

    def __init__(self):
        self.confirm_answer = True
        self.confirm_calls = []
        self.file_answer = ""
        self.unexpected = []  # showerror/showinfo/showwarning: this app must not use them for normal flows


class Harness:
    def __init__(self, window, services, books, users, purchases, connection, search_log, dialogs, callback_errors):
        self.window = window
        self.services = services
        self.books = books
        self.users = users
        self.purchases = purchases
        self.connection = connection
        self.search_log = search_log
        self.dialogs = dialogs
        self.callback_errors = callback_errors

    @property
    def screen(self):
        return self.window._current_screen

    def login(self, username="alice", password="secret"):
        screen = self.screen
        screen.username_var.set(username)
        screen.password_var.set(password)
        click(screen, "Login")
        return self.screen

    def open_catalog(self, username="alice"):
        self.login(username)
        click(self.screen, "Browse catalog")
        return self.screen

    def open_admin(self):
        self.login("admin")
        click(self.screen, "Admin panel")
        return self.screen

    def dialog(self):
        """The single modal dialog currently open on the screen."""
        found = open_dialogs(self.screen)
        assert len(found) == 1, f"expected one open dialog, found {len(found)}"
        return found[0]


@pytest.fixture(scope="session")
def _display():
    tk = pytest.importorskip("tkinter")
    try:
        probe = tk.Tk()
        probe.destroy()
    except tk.TclError:
        pytest.skip("no display available for Tk")


@pytest.fixture
def dialogs(monkeypatch):
    from tkinter import filedialog, messagebox

    fake = Dialogs()

    def ask_yes_no(title, message, **kwargs):
        fake.confirm_calls.append((title, message))
        return fake.confirm_answer

    def ask_open_filename(**kwargs):
        return fake.file_answer

    def unexpected(title=None, message=None, **kwargs):
        fake.unexpected.append((title, message))

    monkeypatch.setattr(messagebox, "askyesno", ask_yes_no)
    monkeypatch.setattr(filedialog, "askopenfilename", ask_open_filename)
    for name in ("showerror", "showinfo", "showwarning"):
        monkeypatch.setattr(messagebox, name, unexpected)
    return fake


@pytest.fixture
def h(_display, dialogs, monkeypatch):
    """A running BookstoreApp on the Login screen with users `alice` (50.00) and `admin` (100.00)."""
    # Admin rights normally come from the ADMIN_USERNAMES env var (and a developer's local .env).
    monkeypatch.setattr("app.services.auth.is_admin", lambda username: username == "admin")

    books = FakeBookRepo()
    users = GuiUserRepo()
    users.create("alice", "secret", Decimal("50.00"))
    users.create("admin", "secret", Decimal("100.00"))
    purchases = FakePurchaseRepo(books)
    connection = FakeConnection()
    search_log = FakeSearchLogRepo()

    services = Services(
        auth=AuthService(users),
        catalog=CatalogService(books, search_log),
        purchase=PurchaseService(books, users, purchases, connection),
        admin=AdminService(books),
    )

    from app.gui.app import BookstoreApp

    window = BookstoreApp(services)
    callback_errors = []
    # An exception inside a button callback must fail the test, not just pop up a dialog.
    window.report_callback_exception = lambda exc, val, tb: callback_errors.append(val)
    window.update()

    harness = Harness(window, services, books, users, purchases, connection, search_log, dialogs, callback_errors)
    try:
        yield harness
    finally:
        window.destroy()
    assert not callback_errors, f"unhandled exception in a GUI callback: {callback_errors!r}"
    assert not dialogs.unexpected, f"unexpected message box: {dialogs.unexpected!r}"
