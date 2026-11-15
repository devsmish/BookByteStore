"""Small helpers for driving Tk screens from tests: find widgets, click buttons, read tables."""
import tkinter as tk
from tkinter import ttk


def walk(widget):
    """Every descendant of `widget`, depth first."""
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def button_texts(widget):
    return sorted(str(w.cget("text")) for w in walk(widget) if isinstance(w, ttk.Button))


def label_texts(widget):
    return [str(w.cget("text")) for w in walk(widget) if isinstance(w, ttk.Label)]


def has_button(widget, text):
    return text in button_texts(widget)


def click(widget, text):
    """Press the button with this exact caption, exactly like a user would, then process pending events."""
    found = [w for w in walk(widget) if isinstance(w, ttk.Button) and str(w.cget("text")) == text]
    assert len(found) == 1, f"expected exactly one button {text!r}, found {len(found)}; buttons: {button_texts(widget)}"
    found[0].invoke()
    widget.update()


def tree_rows(tree):
    """Table content as a list of tuples of strings (Tk may hand numbers back as int, so normalise)."""
    return [tuple(str(v) for v in tree.item(item, "values")) for item in tree.get_children()]


def titles(tree):
    return [row[0] for row in tree_rows(tree)]


def select_row(tree, title):
    """Select the row whose first column equals `title`."""
    for item in tree.get_children():
        if str(tree.item(item, "values")[0]) == title:
            tree.selection_set(item)
            tree.focus(item)
            return
    raise AssertionError(f"no row {title!r} in the table; rows: {titles(tree)}")


def open_dialogs(widget):
    """Toplevel windows (modal dialogs) opened from `widget`."""
    return [w for w in walk(widget) if isinstance(w, tk.Toplevel)]


def color(label):
    return str(label.cget("foreground"))
