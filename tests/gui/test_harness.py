"""The retry helper of the GUI fixtures: it must retry Tcl start-up glitches and nothing else."""
import tkinter

import pytest

from tests.gui.conftest import create_with_retry


class Flaky:
    """A fake window factory that raises `message` for the first `failures` calls."""

    def __init__(self, failures, message):
        self.failures = failures
        self.message = message
        self.calls = 0

    def __call__(self, *args):
        self.calls += 1
        if self.calls <= self.failures:
            raise tkinter.TclError(self.message)
        return args


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("tests.gui.conftest.time.sleep", lambda seconds: None)


@pytest.mark.parametrize(
    "message",
    [
        "Can't find a usable init.tcl in the following directories: ...",
        "Can't find a usable tk.tcl in the following directories: ...",
        "Can't find a usable tk.tcl in the following directories: ... "
        'couldn\'t read file ".../tk8.6/panedwindow.tcl": no such file or directory',
        'invalid command name "tcl_findLibrary"',
    ],
)
def test_start_up_glitches_are_retried(message):
    factory = Flaky(failures=3, message=message)

    with pytest.warns(UserWarning, match="retrying"):
        assert create_with_retry(factory, "services") == ("services",)

    assert factory.calls == 4


def test_different_glitches_in_a_row_are_all_retried():
    messages = iter(["Can't find a usable init.tcl", 'invalid command name "tcl_findLibrary"'])

    def factory():
        try:
            raise tkinter.TclError(next(messages))
        except StopIteration:
            return "window"

    with pytest.warns(UserWarning):
        assert create_with_retry(factory) == "window"


def test_gives_up_after_all_attempts_and_raises_the_error():
    factory = Flaky(failures=99, message="Can't find a usable init.tcl")

    with pytest.warns(UserWarning), pytest.raises(tkinter.TclError, match="init.tcl"):
        create_with_retry(factory, attempts=4)

    assert factory.calls == 4


def test_other_tcl_errors_are_raised_at_once():
    factory = Flaky(failures=99, message="no display name and no $DISPLAY environment variable")

    with pytest.raises(tkinter.TclError, match="no display"):
        create_with_retry(factory)

    assert factory.calls == 1
