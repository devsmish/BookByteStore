from decimal import Decimal
from unittest.mock import MagicMock

from app.db.purchases import PurchaseRepository


def make_connection(fetchall_return=None):
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=False)
    cursor.fetchall.return_value = fetchall_return or []

    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def test_add_purchase_does_not_commit():
    read_conn, _ = make_connection()
    edit_conn, cursor = make_connection()
    repo = PurchaseRepository(read_conn, edit_conn)

    repo.add(1, 2, 3)

    sql = cursor.execute.call_args[0][0]
    assert "INSERT INTO purchases" in sql
    assert not edit_conn.commit.called


def test_get_by_user_maps_rows_to_purchase_objects():
    read_conn, cursor = make_connection(fetchall_return=[
        ("2026-08-19", "Dune", "Herbert", 2, Decimal("10.00"), Decimal("20.00")),
    ])
    edit_conn, _ = make_connection()
    repo = PurchaseRepository(read_conn, edit_conn)

    history = repo.get_by_user(1)

    sql = cursor.execute.call_args[0][0]
    assert "JOIN books" in sql
    assert len(history) == 1
    assert history[0].title == "Dune"
    assert history[0].total == Decimal("20.00")
