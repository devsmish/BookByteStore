"""Admin panel, the add/edit form and the deleted-books screen."""
from decimal import Decimal

import pytest

from app.gui.screens.admin import AdminScreen
from app.gui.screens.deleted_books import DeletedBooksScreen
from app.gui.screens.home import HomeScreen
from app.models import Book
from tests.gui.helpers import click, color, open_dialogs, select_row, titles, tree_rows


@pytest.fixture
def admin(h):
    h.books.add(Book(id=None, title="Emma", author="Austen", price=Decimal("7.50"), stock=3))
    return h.open_admin()


def fill_form(dialog, title, author, price, stock):
    dialog.title_var.set(title)
    dialog.author_var.set(author)
    dialog.price_var.set(price)
    dialog.stock_var.set(stock)


# list

def test_admin_lists_books(admin):
    assert tree_rows(admin.tree) == [
        ("Dune", "Herbert", "$10.00", "5"),
        ("Emma", "Austen", "$7.50", "3"),
    ]


def test_back_returns_home(h, admin):
    click(admin, "Back")
    assert isinstance(h.screen, HomeScreen)


# add

def test_add_book(h, admin):
    click(admin, "Add book")
    dialog = h.dialog()
    assert dialog.title() == "Add book"
    assert dialog.title_var.get() == ""

    fill_form(dialog, "Hamlet", "Shakespeare", "12.5", "4")
    click(dialog, "Save")

    assert open_dialogs(admin) == []
    assert ("Hamlet", "Shakespeare", "$12.50", "4") in tree_rows(admin.tree)


@pytest.mark.parametrize("price, stock", [("abc", "4"), ("5", "x"), ("", ""), ("5", "1.5")])
def test_add_book_with_unparsable_numbers_keeps_the_dialog_open(h, admin, price, stock):
    click(admin, "Add book")
    dialog = h.dialog()
    fill_form(dialog, "Hamlet", "Shakespeare", price, stock)
    click(dialog, "Save")

    assert dialog.error_label.cget("text") == "Invalid price or stock."
    assert open_dialogs(admin) == [dialog]
    assert "Hamlet" not in titles(admin.tree)


@pytest.mark.parametrize(
    "title, author, price, stock, message",
    [
        ("", "Shakespeare", "5", "1", "Title and author cannot be empty"),
        ("Hamlet", "  ", "5", "1", "Title and author cannot be empty"),
        ("Hamlet", "Shakespeare", "-1", "1", "Price and stock cannot be negative"),
        ("Hamlet", "Shakespeare", "5", "-1", "Price and stock cannot be negative"),
    ],
)
def test_add_book_rejected_by_the_service_shows_its_message(h, admin, title, author, price, stock, message):
    click(admin, "Add book")
    dialog = h.dialog()
    fill_form(dialog, title, author, price, stock)
    click(dialog, "Save")

    assert dialog.error_label.cget("text") == message
    assert open_dialogs(admin) == [dialog]
    assert len(h.books.books) == 2


def test_cancel_closes_the_form_without_changes(h, admin):
    click(admin, "Add book")
    dialog = h.dialog()
    fill_form(dialog, "Hamlet", "Shakespeare", "5", "1")
    click(dialog, "Cancel")

    assert open_dialogs(admin) == []
    assert "Hamlet" not in titles(admin.tree)


# edit

def test_edit_without_selection(h, admin):
    click(admin, "Edit selected")

    assert admin.result_label.cget("text") == "Select a book first."
    assert color(admin.result_label) == "red"
    assert open_dialogs(admin) == []


def test_edit_form_is_prefilled(h, admin):
    select_row(admin.tree, "Dune")
    click(admin, "Edit selected")
    dialog = h.dialog()

    assert dialog.title() == "Edit book"
    assert (dialog.title_var.get(), dialog.author_var.get(), dialog.price_var.get(), dialog.stock_var.get()) == (
        "Dune", "Herbert", "10.00", "5",
    )


def test_edit_book_updates_the_table(h, admin):
    select_row(admin.tree, "Dune")
    click(admin, "Edit selected")
    dialog = h.dialog()
    fill_form(dialog, "Dune", "Frank Herbert", "12", "7")
    click(dialog, "Save")

    assert open_dialogs(admin) == []
    assert tree_rows(admin.tree)[0] == ("Dune", "Frank Herbert", "$12.00", "7")
    assert len(h.books.books) == 2  # edited, not duplicated


def test_edit_with_invalid_value_leaves_the_book_unchanged(h, admin):
    select_row(admin.tree, "Dune")
    click(admin, "Edit selected")
    dialog = h.dialog()
    dialog.price_var.set("-3")
    click(dialog, "Save")

    assert dialog.error_label.cget("text") == "Price and stock cannot be negative"
    assert h.books.books[1].price == Decimal("10.00")


# delete

def test_delete_without_selection(h, admin):
    click(admin, "Delete selected")

    assert admin.result_label.cget("text") == "Select a book first."
    assert h.dialogs.confirm_calls == []


def test_delete_cancelled_keeps_the_book(h, admin):
    h.dialogs.confirm_answer = False
    select_row(admin.tree, "Dune")
    click(admin, "Delete selected")

    assert len(h.dialogs.confirm_calls) == 1
    assert "Dune" in h.dialogs.confirm_calls[0][1]
    assert "Dune" in titles(admin.tree)
    assert h.books.books[1].deleted_at is None
    assert admin.result_label.cget("text") == ""


def test_delete_confirmed_removes_the_book(h, admin):
    h.dialogs.confirm_answer = True
    select_row(admin.tree, "Dune")
    click(admin, "Delete selected")

    assert titles(admin.tree) == ["Emma"]
    assert admin.result_label.cget("text") == "Deleted 'Dune'."
    assert color(admin.result_label) == "green"
    assert h.books.books[1].deleted_at is not None  # soft delete


# deleted books / restore

def open_deleted(admin):
    click(admin, "View deleted books")


def test_deleted_screen_with_nothing_deleted(h, admin):
    open_deleted(admin)

    assert isinstance(h.screen, DeletedBooksScreen)
    assert h.screen.result_label.cget("text") == "No deleted books."
    assert tree_rows(h.screen.tree) == []


def test_deleted_book_can_be_restored(h, admin):
    select_row(admin.tree, "Dune")
    click(admin, "Delete selected")
    open_deleted(admin)
    deleted = h.screen

    assert titles(deleted.tree) == ["Dune"]
    select_row(deleted.tree, "Dune")
    click(deleted, "Restore selected")

    assert deleted.result_label.cget("text") == "Restored 'Dune'."
    assert color(deleted.result_label) == "green"
    assert titles(deleted.tree) == []
    assert h.books.books[1].deleted_at is None


def test_restore_without_selection(h, admin):
    select_row(admin.tree, "Dune")
    click(admin, "Delete selected")
    open_deleted(admin)
    click(h.screen, "Restore selected")

    assert h.screen.result_label.cget("text") == "Select a book first."
    assert h.books.books[1].deleted_at is not None


def test_restored_book_is_back_in_the_admin_list(h, admin):
    select_row(admin.tree, "Dune")
    click(admin, "Delete selected")
    open_deleted(admin)
    select_row(h.screen.tree, "Dune")
    click(h.screen, "Restore selected")
    click(h.screen, "Back")

    assert isinstance(h.screen, AdminScreen)
    assert "Dune" in titles(h.screen.tree)


# import

def write_books_file(tmp_path, text):
    path = tmp_path / "books.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_import_adds_new_books_and_merges_existing(h, admin, tmp_path):
    h.dialogs.file_answer = write_books_file(
        tmp_path, "Dune,Herbert,10.00,5\nHamlet,Shakespeare,12.50,3\nnot a valid line\n"
    )
    click(admin, "Import from file...")

    assert admin.result_label.cget("text") == "8 new books loaded."
    assert color(admin.result_label) == "green"
    rows = tree_rows(admin.tree)
    assert ("Dune", "Herbert", "$10.00", "10") in rows  # merged: 5 + 5
    assert ("Hamlet", "Shakespeare", "$12.50", "3") in rows


def test_import_cancelled_changes_nothing(h, admin, tmp_path):
    before = tree_rows(admin.tree)
    h.dialogs.file_answer = ""
    click(admin, "Import from file...")

    assert admin.result_label.cget("text") == ""
    assert tree_rows(admin.tree) == before


def test_import_of_a_missing_file_shows_an_error(h, admin, tmp_path):
    missing = str(tmp_path / "nope.txt")
    h.dialogs.file_answer = missing
    click(admin, "Import from file...")

    assert admin.result_label.cget("text") == f"File not found: {missing}"
    assert color(admin.result_label) == "red"


def test_import_of_a_file_without_valid_rows(h, admin, tmp_path):
    h.dialogs.file_answer = write_books_file(tmp_path, "garbage\nmore,garbage\n")
    click(admin, "Import from file...")

    assert admin.result_label.cget("text") == "0 new books loaded."
    assert len(tree_rows(admin.tree)) == 2
