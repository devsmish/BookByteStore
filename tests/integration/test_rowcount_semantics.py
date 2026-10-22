"""`rowcount` must mean "rows matched", not "rows whose value changed"."""
from decimal import Decimal


def test_saving_a_book_without_changes_is_not_an_error(make_session):
    s = make_session()
    s.admin.add_book("Dune", "Herbert", Decimal("10.00"), 5)
    book = s.admin.list_books()[0]

    s.admin.update_book(book.id, "Dune", "Herbert", Decimal("10.00"), 5)  # identical values: must not raise


def test_a_free_book_can_be_purchased(make_session):
    seed = make_session()
    seed.admin.add_book("Freebie", "Anon", Decimal("0.00"), 3)
    seed.auth.register("alice", "pw", Decimal("10.00"))

    s = make_session()
    user = s.auth.login("alice", "pw")
    book = s.catalog.list_books()[0]

    assert s.purchase.purchase(user.id, book.id, 1) == Decimal("0.00")
