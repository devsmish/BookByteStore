from unittest.mock import MagicMock

import bcrypt

from app.db.users import UserRepository


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
