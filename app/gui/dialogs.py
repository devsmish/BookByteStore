"""A single entry point for yes/no confirmations of destructive actions.

It is deliberately *not* used for informational messages or error alerts.
Throughout the application, these are displayed via inline labels (see
LoginScreen, CatalogScreen, etc.) because a message box blocks the event
loop and requires an actual click. A confirmation, however, must interrupt
the flow and wait for the user's decision.
"""
from tkinter import messagebox


def confirm(parent, title, message):
    return messagebox.askyesno(title, message, parent=parent)
