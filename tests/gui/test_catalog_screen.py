"""Catalog screen: browsing, searching, buying."""
from decimal import Decimal

import pytest

from app.models import Book
from tests.gui.helpers import click, color, label_texts, select_row, titles, tree_rows


@pytest.fixture
def catalog(h):
    h.books.add(Book(id=None, title="Emma", author="Austen", price=Decimal("7.50"), stock=3))
    h.books.add(Book(id=None, title="Sold Out", author="Nobody", price=Decimal("1.00"), stock=0))
    return h.open_catalog()


# browsing

def test_catalog_lists_books_in_stock_only(catalog):
    assert tree_rows(catalog.tree) == [
        ("Dune", "Herbert", "$10.00", "5"),
        ("Emma", "Austen", "$7.50", "3"),
    ]


def test_catalog_shows_the_users_balance(catalog):
    assert catalog.balance_label.cget("text") == "Balance: $50.00"


# search

def test_search_by_title(h, catalog):
    catalog.search_var.set("dun")
    click(catalog, "Search")

    assert titles(catalog.tree) == ["Dune"]
    assert h.search_log.logged == ["dun"]


def test_search_by_author_ignores_case(catalog):
    catalog.search_var.set("AUSTEN")
    click(catalog, "Search")

    assert titles(catalog.tree) == ["Emma"]


def test_search_without_matches_shows_an_empty_table_and_no_warning(catalog):
    catalog.search_var.set("zzz")
    click(catalog, "Search")

    assert titles(catalog.tree) == []
    assert catalog.warning_label.cget("text") == ""


@pytest.mark.parametrize("query", ["", "   "])
def test_empty_search_query_shows_a_warning_and_is_not_logged(h, catalog, query):
    catalog.search_var.set(query)
    click(catalog, "Search")

    assert catalog.warning_label.cget("text") == "Search query cannot be empty"
    assert h.search_log.logged == []


def test_search_log_failure_warns_but_still_shows_results(h, catalog):
    h.search_log.fail = True
    catalog.search_var.set("dune")
    click(catalog, "Search")

    assert "mongo down" in catalog.warning_label.cget("text")
    assert titles(catalog.tree) == ["Dune"]


def test_warning_is_cleared_by_the_next_good_search(h, catalog):
    h.search_log.fail = True
    catalog.search_var.set("dune")
    click(catalog, "Search")
    h.search_log.fail = False
    click(catalog, "Search")

    assert catalog.warning_label.cget("text") == ""


def test_show_all_restores_the_full_list_and_clears_the_warning(catalog):
    catalog.search_var.set("")
    click(catalog, "Search")
    catalog.search_var.set("dune")
    click(catalog, "Search")
    click(catalog, "Show all")

    assert titles(catalog.tree) == ["Dune", "Emma"]
    assert catalog.warning_label.cget("text") == ""


# purchase

def buy(catalog, title, quantity):
    select_row(catalog.tree, title)
    catalog.quantity_var.set(str(quantity))
    click(catalog, "Buy selected")


def test_buy_without_selection(catalog):
    click(catalog, "Buy selected")

    assert catalog.purchase_result_label.cget("text") == "Select a book first."
    assert color(catalog.purchase_result_label) == "red"


@pytest.mark.parametrize("quantity", ["0", "-1", "abc", "", "1.5"])
def test_buy_with_invalid_quantity(h, catalog, quantity):
    buy(catalog, "Dune", quantity)

    assert catalog.purchase_result_label.cget("text") == "Quantity must be a positive whole number."
    assert catalog.balance_label.cget("text") == "Balance: $50.00"
    assert h.purchases.log == []


def test_buy_more_than_in_stock(h, catalog):
    buy(catalog, "Dune", 6)

    assert catalog.purchase_result_label.cget("text") == "Not enough stock for 'Dune'"
    assert color(catalog.purchase_result_label) == "red"
    assert catalog.balance_label.cget("text") == "Balance: $50.00"
    assert h.purchases.log == []


def test_buy_with_insufficient_balance(h):
    h.users.create("poor", "secret", Decimal("5.00"))
    catalog = h.open_catalog("poor")

    buy(catalog, "Dune", 1)  # costs 10.00, the user has 5.00

    assert catalog.purchase_result_label.cget("text") == "Insufficient balance"
    assert color(catalog.purchase_result_label) == "red"
    assert catalog.balance_label.cget("text") == "Balance: $5.00"
    assert h.purchases.log == []
    assert h.connection.rolled_back
    assert not h.connection.committed


def test_successful_purchase_updates_balance_stock_and_message(h, catalog):
    buy(catalog, "Dune", 2)

    assert catalog.balance_label.cget("text") == "Balance: $30.00"
    assert catalog.purchase_result_label.cget("text") == "Bought 2 x 'Dune' for $20.00."
    assert color(catalog.purchase_result_label) == "green"
    assert tree_rows(catalog.tree)[0] == ("Dune", "Herbert", "$10.00", "3")
    assert h.connection.committed
    assert h.users.get_balance(1) == Decimal("30.00")
    assert len(h.purchases.log) == 1


def test_buying_the_last_copies_removes_the_book_from_the_catalog(catalog):
    buy(catalog, "Dune", 5)

    assert titles(catalog.tree) == ["Emma"]
    assert catalog.balance_label.cget("text") == "Balance: $0.00"


def test_two_purchases_in_a_row(catalog):
    buy(catalog, "Dune", 1)
    buy(catalog, "Emma", 2)

    assert catalog.balance_label.cget("text") == "Balance: $25.00"
    assert tree_rows(catalog.tree) == [
        ("Dune", "Herbert", "$10.00", "4"),
        ("Emma", "Austen", "$7.50", "1"),
    ]


def test_new_search_clears_the_previous_purchase_message(catalog):
    buy(catalog, "Dune", 1)
    catalog.search_var.set("emma")
    click(catalog, "Search")

    assert catalog.purchase_result_label.cget("text") == ""


def test_new_balance_is_kept_when_navigating_home(h, catalog):
    buy(catalog, "Dune", 2)
    click(catalog, "Back")

    assert "Balance: $30.00" in label_texts(h.screen)
