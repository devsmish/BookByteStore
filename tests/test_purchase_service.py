from decimal import Decimal

import pytest

from app.exceptions import (
    BookNotFoundError,
    InsufficientBalanceError,
    InsufficientStockError,
    InvalidInputError,
)
from app.models import User
from app.services.purchase_service import PurchaseService


@pytest.fixture
def user1(user_repo):
    user_repo.users[1] = User(id=1, username="alice", balance=Decimal("100.00"))
    return user_repo.users[1]


@pytest.fixture
def purchase_service(book_repo, user_repo, purchase_repo, connection):
    return PurchaseService(book_repo, user_repo, purchase_repo, connection)


def test_purchase_success(purchase_service, book_repo, user_repo, connection, user1):
    total = purchase_service.purchase(1, 1, 2)
    assert total == Decimal("20.00")
    assert book_repo.books[1].stock == 3
    assert user_repo.users[1].balance == Decimal("80.00")
    assert connection.committed is True


def test_purchase_book_not_found(purchase_service, user1):
    with pytest.raises(BookNotFoundError):
        purchase_service.purchase(1, 999, 1)


def test_purchase_insufficient_stock(purchase_service, user1):
    with pytest.raises(InsufficientStockError):
        purchase_service.purchase(1, 1, 999)


def test_purchase_insufficient_balance(purchase_service, book_repo, user1):
    book_repo.books[1].price = Decimal("1000.00")
    with pytest.raises(InsufficientBalanceError):
        purchase_service.purchase(1, 1, 1)


def test_purchase_zero_quantity_rejected(purchase_service, user1):
    with pytest.raises(InvalidInputError):
        purchase_service.purchase(1, 1, 0)


def test_purchase_negative_quantity_rejected(purchase_service, user1):
    with pytest.raises(InvalidInputError):
        purchase_service.purchase(1, 1, -3)


def test_purchase_rolls_back_on_failure(purchase_service, connection, user1):
    with pytest.raises(InsufficientStockError):
        purchase_service.purchase(1, 1, 999)
    assert connection.rolled_back is True
    assert connection.committed is False


def test_history_returns_purchases(purchase_service, user1):
    purchase_service.purchase(1, 1, 1)
    history = purchase_service.history(1)
    assert len(history) == 1
    assert history[0].title == "Dune"


def test_top_up_increases_balance(purchase_service, user1):
    new_balance = purchase_service.top_up(1, Decimal("50.00"))
    assert new_balance == Decimal("150.00")


def test_top_up_rejects_zero(purchase_service, user1):
    with pytest.raises(InvalidInputError):
        purchase_service.top_up(1, Decimal("0"))


def test_top_up_rejects_negative(purchase_service, user1):
    with pytest.raises(InvalidInputError):
        purchase_service.top_up(1, Decimal("-5"))


def test_soft_deleted_book_cannot_be_purchased(purchase_service, book_repo, user1):
    book_repo.delete(1)
    with pytest.raises(BookNotFoundError):
        purchase_service.purchase(1, 1, 1)


def test_purchase_history_survives_book_deletion(purchase_service, book_repo, user1):
    purchase_service.purchase(1, 1, 1)
    book_repo.delete(1)
    history = purchase_service.history(1)
    assert len(history) == 1
    assert history[0].title == "Dune"
