"""A long-lived read connection must always see data committed by the edit connection."""
from decimal import Decimal


def test_top_up_returns_the_fresh_balance(make_session):
    seed = make_session()
    seed.auth.register("alice", "pw", Decimal("100.00"))

    s = make_session()
    user = s.auth.login("alice", "pw")

    assert s.purchase.top_up(user.id, Decimal("50.00")) == Decimal("150.00")
    # logging in again inside the same running process must show the new balance too
    assert s.auth.login("alice", "pw").balance == Decimal("150.00")


def test_user_can_log_in_right_after_registering(make_session):
    s = make_session()
    s.auth.register("alice", "pw", Decimal("1.00"))

    assert s.auth.login("alice", "pw").username == "alice"


def test_admin_sees_their_own_changes_immediately(make_session):
    s = make_session()
    s.admin.add_book("Dune", "Herbert", Decimal("10.00"), 5)
    books = s.admin.list_books()
    assert [b.title for b in books] == ["Dune"]

    book_id = books[0].id
    s.admin.update_book(book_id, "Dune", "Herbert", Decimal("25.00"), 5)
    assert s.admin.list_books()[0].price == Decimal("25.00")

    s.admin.delete_book(book_id)
    assert s.admin.list_books() == []
    assert [b.title for b in s.admin.list_deleted_books()] == ["Dune"]

    s.admin.restore_book(book_id)
    assert [b.title for b in s.admin.list_books()] == ["Dune"]


def test_purchase_is_charged_at_the_current_price(make_session):
    seed = make_session()
    seed.admin.add_book("Dune", "Herbert", Decimal("10.00"), 5)
    seed.auth.register("alice", "pw", Decimal("100.00"))

    s = make_session()
    user = s.auth.login("alice", "pw")
    book = s.catalog.list_books()[0]
    s.admin.update_book(book.id, "Dune", "Herbert", Decimal("25.00"), 5)  # price changes after the session started

    assert s.purchase.purchase(user.id, book.id, 1) == Decimal("25.00")
    assert s.purchase.top_up(user.id, Decimal("0.01")) == Decimal("75.01")  # 100 - 25 + 0.01


def test_history_and_stock_reflect_a_purchase_immediately(make_session):
    seed = make_session()
    seed.admin.add_book("Dune", "Herbert", Decimal("10.00"), 5)
    seed.auth.register("alice", "pw", Decimal("100.00"))

    s = make_session()
    user = s.auth.login("alice", "pw")
    book = s.catalog.list_books()[0]
    s.purchase.purchase(user.id, book.id, 2)

    assert len(s.purchase.history(user.id)) == 1
    assert [b.stock for b in s.catalog.list_books()] == [3]
