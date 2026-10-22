from decimal import Decimal

import pytest

from app.exceptions import BookNotFoundError, InvalidInputError
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


@pytest.mark.parametrize("title,author,price,stock", [
    ("T" * 201, "A", Decimal("1.00"), 1),
    ("T", "A" * 101, Decimal("1.00"), 1),
    ("T", "A", Decimal("100000000.00"), 1),
    ("T", "A", Decimal("1.00"), 2_147_483_648),
])
def test_add_book_rejects_values_that_do_not_fit_the_schema(admin_service, title, author, price, stock):
    with pytest.raises(InvalidInputError):
        admin_service.add_book(title, author, price, stock)


def test_add_book_accepts_the_schema_maximums(admin_service, book_repo):
    admin_service.add_book("T" * 200, "A" * 100, Decimal("99999999.99"), 2_147_483_647)
    assert len(book_repo.books) == 2


def test_import_ignores_a_utf8_bom(admin_service, book_repo, tmp_path):
    path = tmp_path / "books.txt"
    path.write_bytes(b"\xef\xbb\xbfFresh,Author,5.00,2\n")

    admin_service.import_from_file(str(path))

    assert any(b.title == "Fresh" for b in book_repo.books.values())


def test_import_skips_rows_that_would_violate_the_schema(admin_service, book_repo, tmp_path):
    path = tmp_path / "books.txt"
    path.write_text(
        "Good,Author,5.00,2\n"
        ",NoTitle,5.00,2\n"            # empty title
        "Negative,Author,5.00,-3\n"    # negative stock
        "Huge,Author,1e50,1\n"         # does not fit DECIMAL(10,2)
        + "L" * 201 + ",Author,5.00,1\n"  # title longer than the column
    )

    added = admin_service.import_from_file(str(path))

    assert added == 2
    assert sorted(b.title for b in book_repo.books.values()) == ["Dune", "Good"]


def test_import_rolls_back_everything_if_it_fails_midway(admin_service, book_repo, tmp_path, monkeypatch):
    path = tmp_path / "books.txt"
    path.write_text("One,Author,5.00,1\nTwo,Author,5.00,1\n")
    calls = []
    original = book_repo.upsert_by_title_author

    def fail_on_second(*args, **kwargs):
        calls.append(args)
        if len(calls) == 2:
            raise RuntimeError("connection lost")
        return original(*args, **kwargs)

    monkeypatch.setattr(book_repo, "upsert_by_title_author", fail_on_second)

    with pytest.raises(RuntimeError):
        admin_service.import_from_file(str(path))

    assert book_repo.rolled_back is True
