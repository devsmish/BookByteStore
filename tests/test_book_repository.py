from decimal import Decimal
from unittest.mock import MagicMock

from app.db.books import BookRepository


def make_connection(fetchall_return=None, fetchone_return=None, rowcount=1):
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=False)
    cursor.fetchall.return_value = fetchall_return or []
    cursor.fetchone.return_value = fetchone_return
    cursor.rowcount = rowcount

    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def test_get_all_filters_deleted_and_out_of_stock():
    read_conn, cursor = make_connection(
        fetchall_return=[(1, "Dune", "Herbert", Decimal("10.00"), 5, None)]
    )
    edit_conn, _ = make_connection()
    repo = BookRepository(read_conn, edit_conn)

    books = repo.get_all()

    sql = cursor.execute.call_args[0][0]
    assert "stock > 0" in sql
    assert "deleted_at IS NULL" in sql
    assert len(books) == 1
    assert books[0].title == "Dune"


def test_search_filters_deleted():
    read_conn, cursor = make_connection(fetchall_return=[])
    edit_conn, _ = make_connection()
    repo = BookRepository(read_conn, edit_conn)

    repo.search("dune")

    sql = cursor.execute.call_args[0][0]
    assert "deleted_at IS NULL" in sql


def test_get_by_id_excludes_deleted_by_default():
    read_conn, cursor = make_connection(
        fetchone_return=(1, "Dune", "Herbert", Decimal("10.00"), 5, None)
    )
    edit_conn, _ = make_connection()
    repo = BookRepository(read_conn, edit_conn)

    repo.get_by_id(1)

    sql = cursor.execute.call_args[0][0]
    assert "deleted_at IS NULL" in sql


def test_get_by_id_can_include_deleted():
    read_conn, cursor = make_connection(
        fetchone_return=(1, "Dune", "Herbert", Decimal("10.00"), 5, "2026-01-01")
    )
    edit_conn, _ = make_connection()
    repo = BookRepository(read_conn, edit_conn)

    book = repo.get_by_id(1, include_deleted=True)

    sql = cursor.execute.call_args[0][0]
    assert "deleted_at IS NULL" not in sql
    assert book.title == "Dune"


def test_delete_is_soft_not_hard():
    read_conn, _ = make_connection()
    edit_conn, cursor = make_connection(rowcount=1)
    repo = BookRepository(read_conn, edit_conn)

    result = repo.delete(1)

    sql = cursor.execute.call_args[0][0]
    assert "UPDATE books" in sql
    assert "deleted_at = NOW()" in sql
    assert "DELETE FROM" not in sql
    assert result == 1
    assert edit_conn.commit.called


def test_decrease_stock_excludes_deleted_and_does_not_commit():
    read_conn, _ = make_connection()
    edit_conn, cursor = make_connection(rowcount=1)
    repo = BookRepository(read_conn, edit_conn)

    repo.decrease_stock(1, 2)

    sql = cursor.execute.call_args[0][0]
    assert "deleted_at IS NULL" in sql
    assert not edit_conn.commit.called


def test_restore_clears_deleted_at():
    read_conn, _ = make_connection()
    edit_conn, cursor = make_connection(rowcount=1)
    repo = BookRepository(read_conn, edit_conn)

    result = repo.restore(1)

    sql = cursor.execute.call_args[0][0]
    assert "deleted_at = NULL" in sql
    assert result == 1
    assert edit_conn.commit.called
