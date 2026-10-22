from unittest.mock import MagicMock

import bcrypt

from app.db.users import UserRepository
from app.limits import MAX_MONEY


def make_connection(fetchone_return=None, rowcount=1, lastrowid=1):
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=False)
    cursor.fetchone.return_value = fetchone_return
    cursor.rowcount = rowcount
    cursor.lastrowid = lastrowid

    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def test_create_hashes_password_not_plaintext():
    read_conn, _ = make_connection()
    edit_conn, cursor = make_connection(lastrowid=42)
    repo = UserRepository(read_conn, edit_conn)

    user_id = repo.create("alice", "secret123", 100)

    assert user_id == 42
    stored_password = cursor.execute.call_args[0][1][1]  # (username, password, balance)
    assert stored_password != "secret123"
    assert bcrypt.checkpw("secret123".encode("utf-8"), stored_password.encode("utf-8"))


def test_authenticate_correct_password():
    hashed = bcrypt.hashpw("secret123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    read_conn, _ = make_connection(fetchone_return=(1, "alice", hashed, 100))
    edit_conn, _ = make_connection()
    repo = UserRepository(read_conn, edit_conn)

    user = repo.authenticate("alice", "secret123")

    assert user is not None
    assert user.username == "alice"


def test_authenticate_wrong_password():
    hashed = bcrypt.hashpw("secret123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    read_conn, _ = make_connection(fetchone_return=(1, "alice", hashed, 100))
    edit_conn, _ = make_connection()
    repo = UserRepository(read_conn, edit_conn)

    user = repo.authenticate("alice", "wrongpass")

    assert user is None


def test_authenticate_unknown_user_returns_none():
    read_conn, _ = make_connection(fetchone_return=None)
    edit_conn, _ = make_connection()
    repo = UserRepository(read_conn, edit_conn)

    assert repo.authenticate("ghost", "pw") is None


def test_authenticate_selects_explicit_columns_not_star():
    """`SELECT *` + positional unpacking breaks whenever the table has a different number of
    columns (e.g. a database created before `is_admin` was added)."""
    read_conn, cursor = make_connection(fetchone_return=None)
    edit_conn, _ = make_connection()

    UserRepository(read_conn, edit_conn).authenticate("alice", "pw")

    sql = cursor.execute.call_args[0][0]
    assert "*" not in sql
    assert "id, username, password, balance" in " ".join(sql.split())


def test_authenticate_keeps_working_for_passwords_longer_than_72_bytes():
    """Accounts created with bcrypt 4.x have a hash of the first 72 bytes only. bcrypt 5.x raises
    ValueError for longer input, so the repository must hand it at most 72 bytes."""
    password = "x" * 72 + "TAIL"
    hashed = bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")
    read_conn, _ = make_connection(fetchone_return=(1, "alice", hashed, 100))
    edit_conn, _ = make_connection()

    user = UserRepository(read_conn, edit_conn).authenticate("alice", password)

    assert user is not None


def test_increase_balance_refuses_to_exceed_the_column_maximum():
    read_conn, _ = make_connection()
    edit_conn, cursor = make_connection(rowcount=1)

    UserRepository(read_conn, edit_conn).increase_balance(7, 50)

    sql, params = cursor.execute.call_args[0]
    assert "balance + %s <=" in " ".join(sql.split())
    assert MAX_MONEY in params
    assert edit_conn.commit.called
