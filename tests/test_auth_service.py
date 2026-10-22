from decimal import Decimal

import pytest

from app.exceptions import InvalidCredentialsError, InvalidInputError, UsernameTakenError
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


def test_register_rejects_too_long_username(auth_service):
    with pytest.raises(InvalidInputError):
        auth_service.register("u" * 101, "pw", Decimal("1"))


def test_register_accepts_longest_allowed_username(auth_service):
    assert auth_service.register("u" * 100, "pw", Decimal("1")).username == "u" * 100


def test_register_rejects_balance_that_does_not_fit_the_column(auth_service):
    with pytest.raises(InvalidInputError):
        auth_service.register("bob", "pw", Decimal("100000000.00"))


def test_register_rejects_password_longer_than_bcrypt_can_use(auth_service):
    """bcrypt only uses the first 72 bytes (4.x silently ignores the rest, 5.x raises ValueError)."""
    with pytest.raises(InvalidInputError):
        auth_service.register("bob", "x" * 73, Decimal("1"))
    with pytest.raises(InvalidInputError):
        auth_service.register("bob", "я" * 37, Decimal("1"))  # 74 bytes in UTF-8


def test_register_accepts_a_72_byte_password(auth_service):
    assert auth_service.register("bob", "x" * 72, Decimal("1")).username == "bob"
