# Building an executable (Windows)

Packs `../app/gui_main.py` into a single `.exe` with PyInstaller - for the case when the GUI is needed on a
machine without Python.

## Build

```bash
pip install -r requirements-build.txt
python build_scripts/build.py
```

Result: `dist/BookByteStore.exe` (on Windows) with `../.env.example` copied next to it.

## First run of the exe

1. Copy `../.env.example` to `.env` **next to `BookByteStore.exe`** and fill it in (DB credentials etc.)
2. Make sure MySQL and MongoDB are reachable (e.g. `docker compose up -d`, or point `../.env` at existing servers)
3. Run `BookByteStore.exe`

The exe finds `../.env` and writes `bookstore.log` **next to itself**, no matter which folder it was started
from (shortcut, double-click, terminal). That is what `app/env.py` is for. Do not set a relative `LOG_FILE`
in `.env`: it would be resolved against the folder the app was started from.

## Why `../.env` is not inside the exe

PyInstaller can pack files into the archive (`datas`), but they are unpacked to a temporary folder on every
run: you could not edit `../.env` there, and it holds credentials that must not be baked into a binary.

## What the exe does NOT make safer

The application talks to the database directly, so **everyone who runs it needs database credentials with
write access** - and can use them to change balances or read password hashes without the app. That is fine for
a course project or a demo; to hand the app to untrusted users you would need a server layer between the GUI
and the database.

## Notes

- An unsigned exe may be flagged by Windows SmartScreen or an antivirus on first run. This is typical for
  PyInstaller builds and is not a build error. UPX compression is disabled in `bookstore.spec` to reduce this.
- No icon is set (add a `.ico` file and `icon=...` in `bookstore.spec`).
