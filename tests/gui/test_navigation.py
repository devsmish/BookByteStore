"""Home screen and moving between screens."""
from app.gui.screens.admin import AdminScreen
from app.gui.screens.catalog import CatalogScreen
from app.gui.screens.history import HistoryScreen
from app.gui.screens.home import HomeScreen
from app.gui.screens.login import LoginScreen
from tests.gui.helpers import click, has_button, label_texts


def test_home_shows_role_user(h):
    h.login("alice")
    assert "Role: user" in label_texts(h.screen)


def test_home_shows_role_admin(h):
    h.login("admin")
    assert "Role: admin" in label_texts(h.screen)


def test_admin_button_is_visible_only_for_admins(h):
    h.login("alice")
    assert not has_button(h.screen, "Admin panel")

    click(h.screen, "Log out")
    h.login("admin")
    assert has_button(h.screen, "Admin panel")


def test_home_catalog_home(h):
    h.login("alice")
    click(h.screen, "Browse catalog")
    assert isinstance(h.screen, CatalogScreen)

    click(h.screen, "Back")
    assert isinstance(h.screen, HomeScreen)


def test_home_history_home(h):
    h.login("alice")
    click(h.screen, "Purchase history")
    assert isinstance(h.screen, HistoryScreen)

    click(h.screen, "Back")
    assert isinstance(h.screen, HomeScreen)


def test_catalog_and_history_keep_the_same_user(h):
    h.login("alice")
    click(h.screen, "Browse catalog")
    assert h.screen.user.username == "alice"
    click(h.screen, "Back")
    click(h.screen, "Purchase history")
    assert h.screen.user.username == "alice"


def test_logout_returns_to_an_empty_login_screen(h):
    h.login("alice")
    click(h.screen, "Log out")

    assert isinstance(h.screen, LoginScreen)
    assert h.screen.username_var.get() == ""
    assert h.screen.password_var.get() == ""


def test_admin_panel_and_back_to_home(h):
    h.login("admin")
    click(h.screen, "Admin panel")
    assert isinstance(h.screen, AdminScreen)

    click(h.screen, "Back")
    assert isinstance(h.screen, HomeScreen)


def test_only_one_screen_exists_after_navigation(h):
    h.login("alice")
    for _ in range(3):
        click(h.screen, "Browse catalog")
        click(h.screen, "Back")

    assert len(h.window._container.winfo_children()) == 1
