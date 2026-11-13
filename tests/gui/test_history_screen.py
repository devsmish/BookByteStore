"""Purchase history screen."""
from tests.gui.helpers import click, select_row, tree_rows


def test_history_of_a_new_user_is_empty(h):
    h.login("alice")
    click(h.screen, "Purchase history")

    assert h.screen.info_label.cget("text") == "No purchases yet."
    assert tree_rows(h.screen.tree) == []


def test_purchase_shows_up_in_history(h):
    catalog = h.open_catalog()
    select_row(catalog.tree, "Dune")
    catalog.quantity_var.set("2")
    click(catalog, "Buy selected")

    click(h.screen, "Back")
    click(h.screen, "Purchase history")

    assert h.screen.info_label.cget("text") == ""
    assert tree_rows(h.screen.tree) == [("2026-08-19", "Dune", "Herbert", "2", "$10.00", "$20.00")]
