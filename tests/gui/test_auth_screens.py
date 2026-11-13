"""Login and registration screens."""
from decimal import Decimal

from app.gui.screens.home import HomeScreen
from app.gui.screens.login import LoginScreen
from app.gui.screens.register import RegisterScreen
from tests.gui.helpers import click, color, label_texts


def fill_login(screen, username, password):
    screen.username_var.set(username)
    screen.password_var.set(password)


def fill_register(screen, username, password, balance="0"):
    screen.username_var.set(username)
    screen.password_var.set(password)
    screen.balance_var.set(balance)


# login

def test_app_starts_on_the_login_screen(h):
    assert isinstance(h.screen, LoginScreen)


def test_login_success_opens_home(h):
    h.login("alice", "secret")

    assert isinstance(h.screen, HomeScreen)
    assert "Welcome, alice!" in label_texts(h.screen)
    assert "Balance: $50.00" in label_texts(h.screen)


def test_login_wrong_password_shows_error_and_stays(h):
    screen = h.screen
    fill_login(screen, "alice", "wrong")
    click(screen, "Login")

    assert h.screen is screen
    assert screen.error_label.cget("text") == "Invalid username or password"
    assert color(screen.error_label) == "red"


def test_login_unknown_user_shows_the_same_error(h):
    screen = h.screen
    fill_login(screen, "nobody", "secret")
    click(screen, "Login")

    assert screen.error_label.cget("text") == "Invalid username or password"


def test_login_empty_fields_show_error(h):
    screen = h.screen
    click(screen, "Login")

    assert isinstance(h.screen, LoginScreen)
    assert screen.error_label.cget("text") == "Invalid username or password"


def test_password_field_is_masked(h):
    entries = [w for w in h.screen.winfo_children()[0].winfo_children() if w.winfo_class() == "TEntry"]
    assert [str(e.cget("show")) for e in entries] == ["", "*"]


def test_login_screen_has_no_message_by_default(h):
    assert not any("Registration" in text for text in label_texts(h.screen))


# registration

def test_register_instead_opens_registration_and_back_returns(h):
    click(h.screen, "Register instead")
    assert isinstance(h.screen, RegisterScreen)

    click(h.screen, "Back to login")
    assert isinstance(h.screen, LoginScreen)


def test_register_success_returns_to_login_with_message(h):
    click(h.screen, "Register instead")
    fill_register(h.screen, "bob", "pw123", "25")
    click(h.screen, "Register")

    assert isinstance(h.screen, LoginScreen)
    assert "Registration successful — please log in." in label_texts(h.screen)
    created = [u for u in h.users.users.values() if u.username == "bob"]
    assert len(created) == 1
    assert created[0].balance == Decimal("25.00")


def test_registered_user_can_log_in(h):
    click(h.screen, "Register instead")
    fill_register(h.screen, "bob", "pw123", "25")
    click(h.screen, "Register")

    h.login("bob", "pw123")

    assert isinstance(h.screen, HomeScreen)
    assert "Welcome, bob!" in label_texts(h.screen)
    assert "Balance: $25.00" in label_texts(h.screen)


def test_register_taken_username_shows_error(h):
    click(h.screen, "Register instead")
    screen = h.screen
    fill_register(screen, "alice", "pw123")
    click(screen, "Register")

    assert h.screen is screen
    assert screen.error_label.cget("text") == "Username 'alice' is already taken"


def test_register_empty_fields_show_error(h):
    click(h.screen, "Register instead")
    screen = h.screen
    fill_register(screen, "", "")
    click(screen, "Register")

    assert h.screen is screen
    assert screen.error_label.cget("text") == "Username and password cannot be empty"


def test_register_invalid_balance_shows_error(h):
    click(h.screen, "Register instead")
    screen = h.screen
    fill_register(screen, "bob", "pw123", "abc")
    click(screen, "Register")

    assert h.screen is screen
    assert screen.error_label.cget("text") == "Invalid balance"
    assert not any(u.username == "bob" for u in h.users.users.values())


def test_register_negative_balance_shows_error(h):
    click(h.screen, "Register instead")
    screen = h.screen
    fill_register(screen, "bob", "pw123", "-5")
    click(screen, "Register")

    assert screen.error_label.cget("text") == "Balance cannot be negative"
    assert not any(u.username == "bob" for u in h.users.users.values())


def test_failed_registration_keeps_what_was_typed(h):
    click(h.screen, "Register instead")
    screen = h.screen
    fill_register(screen, "alice", "pw123", "10")
    click(screen, "Register")

    assert screen.username_var.get() == "alice"
    assert screen.balance_var.get() == "10"
