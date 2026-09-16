from decimal import Decimal

import pytest

from app.exceptions import InvalidInputError, BookNotFoundError
from app.services.admin_service import AdminService


@pytest.fixture
def admin_service(book_repo):
    return AdminService(book_repo)


def test_add_book(admin_service, book_repo):
    admin_service.add_book("New", "Author", Decimal("5.00"), 3)
    assert len(book_repo.books) == 2


def test_add_book_rejects_empty_title(admin_service):
    with pytest.raises(InvalidInputError):
        admin_service.add_book("", "Author", Decimal("5.00"), 3)


def test_add_book_rejects_negative_price(admin_service):
    with pytest.raises(InvalidInputError):
        admin_service.add_book("T", "A", Decimal("-1.00"), 3)


def test_add_book_rejects_negative_stock(admin_service):
    with pytest.raises(InvalidInputError):
        admin_service.add_book("T", "A", Decimal("1.00"), -3)


def test_update_book(admin_service, book_repo):
    admin_service.update_book(1, "Dune (Updated)", "Herbert", Decimal("12.00"), 10)
    assert book_repo.books[1].title == "Dune (Updated)"
    assert book_repo.books[1].price == Decimal("12.00")


def test_update_nonexistent_book_raises(admin_service):
    with pytest.raises(BookNotFoundError):
        admin_service.update_book(999, "T", "A", Decimal("1.00"), 1)


def test_delete_and_restore_book(admin_service, book_repo):
    admin_service.delete_book(1)
    assert book_repo.books[1].deleted_at is not None
    assert len(admin_service.list_deleted_books()) == 1

    admin_service.restore_book(1)
    assert book_repo.books[1].deleted_at is None
    assert admin_service.list_deleted_books() == []


def test_delete_already_deleted_book_raises(admin_service):
    admin_service.delete_book(1)
    with pytest.raises(BookNotFoundError):
        admin_service.delete_book(1)


def test_restore_non_deleted_book_raises(admin_service):
    with pytest.raises(BookNotFoundError):
        admin_service.restore_book(1)


def test_import_from_file_creates_and_merges(admin_service, book_repo, tmp_path):
    file = tmp_path / "books.txt"
    file.write_text(
        "Dune,Herbert,10.00,5\n"            # merges into an existing book
        "New Book,New Author,7.50,2\n"      # creates a new book
        "bad,line,only,three,parts\n"       # skipped: incorrect number of columns
        "Bad Price,Author,notanumber,3\n"   # skipped: invalid price
    )

    added = admin_service.import_from_file(str(file))

    assert added == 5 + 2  # only valid lines are included
    assert book_repo.books[1].stock == 10
    assert any(b.title == "New Book" for b in book_repo.books.values())


def test_import_from_file_missing_file_raises(admin_service):
    with pytest.raises(FileNotFoundError):
        admin_service.import_from_file("/nonexistent/path.txt")
