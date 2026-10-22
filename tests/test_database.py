"""Guards for how connections are opened (root cause of the stale-read / rowcount bugs)."""
from unittest.mock import MagicMock, patch

import pytest
from pymysql.constants import CLIENT

import app.database as database

CFG = {"host": "h", "port": 3306, "user": "u", "password": "p"}


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    monkeypatch.setattr(database, "config_read", dict(CFG))
    monkeypatch.setattr(database, "config_edit", dict(CFG))
    monkeypatch.setattr(database, "db_name", "bookstore_test")


def _kwargs_for(open_connection):
    with patch("app.database.pymysql.connect") as connect:
        open_connection()
    return connect.call_args.kwargs


def test_read_connection_uses_autocommit():
    """Without autocommit the read connection keeps one transaction open forever and,
    under REPEATABLE READ, keeps seeing the data as it was at its first SELECT."""
    assert _kwargs_for(database.get_read_connection)["autocommit"] is True


def test_edit_connection_stays_transactional():
    """The purchase flow relies on commit()/rollback() over several statements."""
    assert not _kwargs_for(database.get_edit_connection).get("autocommit")


@pytest.mark.parametrize("opener", [database.get_read_connection, database.get_edit_connection])
def test_connections_report_matched_rows_not_changed_rows(opener):
    """Services read `rowcount == 0` as "no such row"; without FOUND_ROWS an UPDATE that
    leaves values unchanged (or a free purchase) is reported as 0 rows."""
    assert _kwargs_for(opener)["client_flag"] & CLIENT.FOUND_ROWS


@pytest.mark.parametrize("opener", [database.get_read_connection, database.get_edit_connection, database.init_db])
@pytest.mark.parametrize("bad_name", [None, "", "my-db", "a b", "x`; DROP DATABASE y; --"])
def test_missing_or_unsafe_database_name_is_reported_before_connecting(monkeypatch, opener, bad_name):
    monkeypatch.setattr(database, "db_name", bad_name)
    with patch("app.database.pymysql.connect", new=MagicMock()) as connect:
        with pytest.raises(database.DatabaseConnectionError, match="MYSQL_DB_NAME"):
            opener()
    connect.assert_not_called()  # in particular: no `CREATE DATABASE None`
