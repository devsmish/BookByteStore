"""Общие константы отступов и настройка темы Tkinter."""

PAD = 12          # outer margin for screen sections (top_bar, tree, etc.)
FIELD_PAD = 4     # vertical spacing between form fields


def apply_style(root):
    from tkinter import ttk

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    default_font = ("Segoe UI", 10) if _font_available(root, "Segoe UI") else ("", 10)
    style.configure(".", font=default_font)


def _font_available(root, family):
    import tkinter.font as tkfont
    return family in tkfont.families(root)
