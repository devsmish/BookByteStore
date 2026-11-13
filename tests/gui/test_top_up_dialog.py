"""Top-up dialog, opened from the home screen."""
from decimal import Decimal

import pytest

from app.gui.screens.home import HomeScreen
from tests.gui.helpers import click, label_texts, open_dialogs


@pytest.fixture
def dialog(h):
    h.login("alice")
    click(h.screen, "Top up balance")
    return h.dialog()


def test_dialog_opens_empty(dialog):
    assert dialog.title() == "Top up balance"
    assert dialog.amount_var.get() == ""
    assert dialog.error_label.cget("text") == ""


@pytest.mark.parametrize("raw", ["abc", "", "1e10", "nan"])
def test_invalid_amount(h, dialog, raw):
    dialog.amount_var.set(raw)
    click(dialog, "Top up")

    assert dialog.error_label.cget("text") == "Invalid amount"
    assert h.users.get_balance(1) == Decimal("50.00")
    assert open_dialogs(h.screen) == [dialog]


@pytest.mark.parametrize("raw", ["-5", "0"])
def test_non_positive_amount(h, dialog, raw):
    dialog.amount_var.set(raw)
    click(dialog, "Top up")

    assert dialog.error_label.cget("text") == "Amount must be positive"
    assert h.users.get_balance(1) == Decimal("50.00")
    assert open_dialogs(h.screen) == [dialog]
    assert "Balance: $50.00" in label_texts(h.screen)


def test_success_updates_the_balance_label_of_the_home_screen(h, dialog):
    home = h.screen
    dialog.amount_var.set("25.5")
    click(dialog, "Top up")

    assert isinstance(h.screen, HomeScreen)
    assert "Balance: $75.50" in label_texts(home)
    assert home.user.balance == Decimal("75.50")
    assert h.users.get_balance(1) == Decimal("75.50")
    assert open_dialogs(home) == []


def test_cancel_closes_the_dialog_without_changes(h, dialog):
    home = h.screen
    dialog.amount_var.set("25")
    click(dialog, "Cancel")

    assert open_dialogs(home) == []
    assert "Balance: $50.00" in label_texts(home)
    assert h.users.get_balance(1) == Decimal("50.00")


def test_a_failed_attempt_can_be_corrected_in_the_same_dialog(h, dialog):
    dialog.amount_var.set("abc")
    click(dialog, "Top up")
    dialog.amount_var.set("10")
    click(dialog, "Top up")

    assert "Balance: $60.00" in label_texts(h.screen)
    assert open_dialogs(h.screen) == []


def test_new_balance_is_seen_in_the_catalog(h, dialog):
    dialog.amount_var.set("10")
    click(dialog, "Top up")
    click(h.screen, "Browse catalog")

    assert h.screen.balance_label.cget("text") == "Balance: $60.00"
