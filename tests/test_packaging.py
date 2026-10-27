"""Guards for the PyInstaller setup: mistakes here only show up when you try to build."""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_spec_entry_point_exists():
    spec = (PROJECT_ROOT / "bookstore.spec").read_text(encoding="utf-8")
    entry = re.search(r"Analysis\(\s*\['([^']+)'\]", spec)

    assert entry, "could not find the entry script in bookstore.spec"
    assert (PROJECT_ROOT / entry.group(1)).is_file()


def test_spec_is_not_hidden_by_gitignore():
    """A blanket `*.spec` ignore would keep the build recipe out of git."""
    lines = [line.strip() for line in (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()]

    if "*.spec" in lines:
        assert "!bookstore.spec" in lines[lines.index("*.spec"):]


def test_secrets_and_build_output_stay_out_of_git():
    lines = {line.strip() for line in (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()}

    assert {".env", "build/", "dist/"} <= lines
