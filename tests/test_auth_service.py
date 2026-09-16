from decimal import Decimal

import pytest

from app.exceptions import InvalidInputError, UsernameTakenError, InvalidCredentialsError
from app.services.auth import AuthService


@pytest.fixture
def auth_service(user_repo):
    return AuthService(user_repo)


def test_register_creates_user(auth_service):
    user = auth_service.register("alice", "pw123", Decimal("100"))
    assert user.username == "alice"
    assert user.balance == Decimal("100")
    assert user.id is not None


def test_register_rejects_empty_username(auth_service):
    with pytest.raises(InvalidInputError):
        auth_service.register("", "pw123", Decimal("10"))


def test_register_rejects_empty_password(auth_service):
    with pytest.raises(InvalidInputError):
        auth_service.register("bob", "   ", Decimal("10"))


def test_register_rejects_negative_balance(auth_service):
    with pytest.raises(InvalidInputError):
        auth_service.register("bob", "pw", Decimal("-5"))


def test_register_rejects_duplicate_username(auth_service):
    auth_service.register("alice", "pw", Decimal("10"))
    with pytest.raises(UsernameTakenError):
        auth_service.register("alice", "pw2", Decimal("20"))


def test_login_success(auth_service):
    auth_service.register("alice", "pw123", Decimal("10"))
    user = auth_service.login("alice", "pw123")
    assert user.username == "alice"


def test_login_wrong_password(auth_service):
    auth_service.register("alice", "pw123", Decimal("10"))
    with pytest.raises(InvalidCredentialsError):
        auth_service.login("alice", "wrong")


def test_login_unknown_user(auth_service):
    with pytest.raises(InvalidCredentialsError):
        auth_service.login("ghost", "pw")


def test_login_marks_admin(auth_service, monkeypatch):
    monkeypatch.setattr(
        "app.services.auth.is_admin",
        lambda username: username == "alice",
    )
    auth_service.register("alice", "pw123", Decimal("10"))
    user = auth_service.login("alice", "pw123")
    assert user.is_admin is True


def test_login_non_admin_by_default(auth_service, monkeypatch):
    monkeypatch.setattr("app.services.auth.is_admin", lambda username: False)
    auth_service.register("bob", "pw123", Decimal("10"))
    user = auth_service.login("bob", "pw123")
    assert user.is_admin is False
