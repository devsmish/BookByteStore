"""Integration tests: the real app code against a real MySQL server.

The unit tests use mocked connections, so they cannot see transaction/isolation
behaviour (stale reads on a long-lived connection) or driver semantics
(``cursor.rowcount``). Those bugs only show up on a real DB.

SAFETY: these tests DROP and re-create a database. They therefore
  * never read ``.env``;
  * run only when the dedicated BBS_TEST_DB_* variables are set explicitly;
  * refuse to touch a database whose name does not contain "test".

    BBS_TEST_DB_HOST=127.0.0.1
    BBS_TEST_DB_USER=root
    BBS_TEST_DB_PASSWORD=secret
    BBS_TEST_DB_NAME=bookstore_itest
    pytest tests/integration
"""
import os
import re
from types import SimpleNamespace

import pymysql
import pytest

import app.database as database
from app.db.books import BookRepository
from app.db.purchases import PurchaseRepository
from app.db.users import UserRepository
from app.services.admin_service import AdminService
from app.services.auth import AuthService
from app.services.catalog_service import CatalogService
from app.services.purchase_service import PurchaseService
from tests.conftest import FakeSearchLogRepo

REQUIRED = ("BBS_TEST_DB_HOST", "BBS_TEST_DB_USER", "BBS_TEST_DB_PASSWORD", "BBS_TEST_DB_NAME")


@pytest.fixture
def test_db(monkeypatch):
    missing = [name for name in REQUIRED if not os.getenv(name)]
    if missing:
        pytest.skip("integration tests need a dedicated MySQL: set " + ", ".join(missing))

    name = os.environ["BBS_TEST_DB_NAME"]
    if not re.fullmatch(r"[A-Za-z0-9_]*test[A-Za-z0-9_]*", name):
        pytest.fail(f"refusing to run: BBS_TEST_DB_NAME={name!r} must contain 'test' (the DB is dropped!)")

    cfg = {
        "host": os.environ["BBS_TEST_DB_HOST"],
        "port": int(os.getenv("BBS_TEST_DB_PORT", "3306")),
        "user": os.environ["BBS_TEST_DB_USER"],
        "password": os.environ["BBS_TEST_DB_PASSWORD"],
    }
    # Point the application's own connection factory at the test database.
    monkeypatch.setattr(database, "config_read", dict(cfg))
    monkeypatch.setattr(database, "config_edit", dict(cfg))
    monkeypatch.setattr(database, "db_name", name)

    def drop():
        conn = pymysql.connect(**cfg)
        with conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{name}`")
        conn.commit()
        conn.close()

    drop()
    database.init_db()  # the application's own schema creation
    yield name
    drop()


@pytest.fixture
def make_session(test_db):
    """Builds what one running GUI/CLI process has: one read + one edit connection."""
    opened = []

    def _make(edit_connection=None):
        read = database.get_read_connection()
        edit = edit_connection or database.get_edit_connection()
        opened.extend([read, edit])
        books = BookRepository(read, edit)
        users = UserRepository(read, edit)
        purchases = PurchaseRepository(read, edit)
        return SimpleNamespace(
            auth=AuthService(users),
            catalog=CatalogService(books, FakeSearchLogRepo()),
            purchase=PurchaseService(books, users, purchases, edit),
            admin=AdminService(books),
            read=read,
            edit=edit,
        )

    yield _make
    for conn in opened:
        try:
            conn.close()
        except Exception:
            pass


@pytest.fixture
def raw(test_db):
    """Runs a query on a brand-new connection: always sees the committed truth."""

    def _raw(sql, params=()):
        conn = database.get_edit_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
            conn.commit()
            return rows
        finally:
            conn.close()

    return _raw
