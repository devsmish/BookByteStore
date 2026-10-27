import sys
from pathlib import Path


def get_env_path():
    """Path to the .env file.

    In a normal run (`python -m app.main`) it is the project root. In a PyInstaller build it is the
    folder of the executable itself: when the exe is started from a shortcut or by double-click the
    working directory can be anything, and python-dotenv's default lookup starts from the working
    directory when the app is frozen - so a .env lying right next to the exe would not be found.
    """
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent.parent
    return base_dir / ".env"


def get_base_dir():
    """Folder for files that belong next to the application (e.g. the default log file)."""
    return get_env_path().parent
