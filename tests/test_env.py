"""Where the app looks for .env and writes its log must not depend on the working directory.

A packaged exe is often started from a shortcut or by double-click, where the working directory can be
anything: resolving paths against it makes a perfectly placed .env "disappear".
"""
import logging
import sys
from pathlib import Path

from app import env

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_env_path_in_a_normal_run_is_the_project_root():
    assert env.get_env_path() == PROJECT_ROOT / ".env"


def test_env_path_in_a_frozen_build_is_next_to_the_executable(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "BookByteStore.exe"))

    assert env.get_env_path() == tmp_path.resolve() / ".env"
    assert env.get_base_dir() == tmp_path.resolve()


def test_env_path_ignores_the_working_directory(monkeypatch, tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "BookByteStore.exe"))

    assert env.get_env_path().parent == tmp_path.resolve()


def test_default_log_file_is_next_to_the_application_not_in_the_working_directory(monkeypatch, tmp_path):
    from app import logging_config

    app_dir = tmp_path / "app_dir"
    app_dir.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    monkeypatch.delenv("LOG_FILE", raising=False)
    monkeypatch.setattr(logging_config, "_configured", False)
    monkeypatch.setattr(logging_config, "get_base_dir", lambda: app_dir)

    logger = logging.getLogger("bookstore")
    before = list(logger.handlers)
    logging_config.setup_logging()
    added = [h for h in logger.handlers if h not in before]
    try:
        files = [h.baseFilename for h in added if hasattr(h, "baseFilename")]
        assert files == [str(app_dir / "bookstore.log")]
    finally:
        for handler in added:
            logger.removeHandler(handler)
            handler.close()


def test_env_example_does_not_pin_a_relative_log_path():
    """An active `LOG_FILE=bookstore.log` in .env overrides the sensible default and is then resolved
    against the working directory, so the log lands wherever the app happened to be started from."""
    lines = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()

    assert [line for line in lines if line.strip().startswith("LOG_FILE=")] == []
