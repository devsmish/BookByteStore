"""Builds BookByteStore into a single executable (an .exe on Windows) and stages the files needed
for the first run next to it.

    python build_scripts/build.py

Requires: pip install -r requirements-build.txt
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def main():
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "bookstore.spec", "--noconfirm", "--clean"],
        cwd=ROOT,
        check=True,
    )

    # .env.example goes next to the exe as a plain file (not inside the archive - see bookstore.spec).
    shutil.copy(ROOT / ".env.example", DIST / ".env.example")

    print(f"\nDone. Result: {DIST}")
    print("Before the first run: copy .env.example to .env next to the exe and fill it in.")


if __name__ == "__main__":
    main()
