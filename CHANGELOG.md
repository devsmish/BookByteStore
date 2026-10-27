# Changelog

## v0.7.0 — Windows executable (PyInstaller) — 27/10/2026

### Added
- `bookstore.spec`, `../build_scripts/build.py`, `../build_scripts/README.md`, `../requirements-build.txt` — one-file
  GUI build (`python build_scripts/build.py`); `.env.example` is staged next to the exe.
- `../app/env.py` — `get_env_path()` / `get_base_dir()`: the `.env` file and the default log file are resolved
  relative to the application (the exe when packaged), not the working directory.
- `../tests/test_env.py`, `../tests/test_packaging.py` — guards for the path resolution and for the build recipe.

### Fixed
- A packaged exe could not find a `.env` lying next to it when started from another folder (shortcut,
  double-click): python-dotenv starts its search from the working directory in a frozen app. All four
  `load_dotenv()` calls now use the explicit path.
- `.env.example` pinned `LOG_FILE=bookstore.log`; copied to `.env` it overrode the default and, being relative,
  put the log into whatever folder the app was started from. The variable is now commented out.
- `.gitignore` contained `*.spec`, which would have kept `bookstore.spec` out of git; added `!bookstore.spec`.

### Changed
- README: the `UserRepository` description no longer mentions the removed 5-column tuple unpacking.

## v0.6.0 — Bug fixes after a control review — 22/10/2026

### Fixed
- **Stale data on the read connection.** The read connection kept one transaction open for the whole
  session, so under MySQL's default `REPEATABLE READ` it kept seeing the data as of its first `SELECT`
  and never the commits made through the edit connection. Visible effects, all reproduced on a real
  MySQL 8.0: the balance did not change on the form after a top-up (only restarting the app helped);
  a user could not log in right after registering; the admin panel did not show a book just added,
  edited or deleted; the purchase history and stock were not refreshed after a purchase; and a
  purchase was **charged at the old price** after an admin changed it. The read connection now uses
  `autocommit`.
- **`cursor.rowcount` meant "rows changed", not "rows matched".** Saving a book without edits
  reported "Book not found"; buying a free (0.00) book reported "Insufficient balance". Connections
  now use `CLIENT.FOUND_ROWS`.
- **Half-finished purchase could be committed later.** On any exception that is not a
  `BookstoreError` (lock timeout, lost connection, ...) there was no rollback, so the next unrelated
  commit persisted the partial purchase (stock and balance written off, no purchase record). Any error
  now rolls back. The same applies to a failed file import.
- **Login crashed** (`ValueError: not enough values to unpack`) on a database whose `users` table was
  created before the `is_admin` column existed. `authenticate` now selects explicit columns.
- **A missing `MYSQL_DB_NAME` silently ran `CREATE DATABASE None`.** It is now reported clearly and
  the name is validated and quoted.
- **Input that did not fit the schema leaked raw driver errors** (or was silently truncated on servers
  without STRICT mode): `NaN`/`Infinity`/`1e50`, amounts over `99999999.99`, titles over 200 and
  authors/usernames over 100 characters, stock over `INT`. Passwords over 72 bytes were silently cut
  by `bcrypt` 4.x (and raise `ValueError` on 5.x). These are now domain errors with clear messages.
- **File import:** a UTF-8 BOM (Excel "CSV UTF-8", older Notepad) ended up inside the first title;
  rows with empty/negative/out-of-range values are now skipped like other invalid rows.
- **GUI:** an unhandled exception in a Tk callback was invisible in a windowed app (the button simply
  did nothing and nothing reached the log). It is now logged and shown in an error dialog.
- `requirements.txt` was saved as UTF-16; converted to UTF-8 so tools such as Dependabot can read it.

### Added
- `../app/limits.py` — limits that mirror the database schema.
- `tests/integration` — 17 tests that run the real code against a real MySQL (opt-in, see README).
- `../tests/test_database.py`, `../tests/test_gui_robustness.py`, and new unit tests for every fix above.
- CI job `integration` (MySQL 8.0 service container).

### Changed
- `top_up` refuses an amount that would push the balance over `DECIMAL(10,2)`; the limit is checked
  atomically inside the `UPDATE`.
- `UserRepository.authenticate` hands at most 72 bytes to `bcrypt`, so accounts created with long
  passwords keep working on both `bcrypt` 4.x and 5.x.

## v0.5.7 — Robustness and polish — 08/10/2026

### Added
- `gui/dialogs.py` — `confirm()`, a unified point for yes/no confirmations (used when deleting a book)
- `gui/style.py` — `clam` theme, shared font with fallback, `PAD` constant

### Changed
- `AdminScreen._delete_selected`: now requests confirmation before deletion (matching CLI behavior)
- `BookstoreApp`: applies `apply_style()` on startup
- `catalog.py`, `history.py`, `admin.py`, `deleted_books.py`: `padx=12` → `PAD`

## v0.5.6 — Admin panel — 06/10/2026

### Added
- `gui/screens/admin.py` — admin panel hub
- `gui/screens/book_form_dialog.py` — unified modal for adding/editing books
- `gui/screens/deleted_books.py` — screen for soft-deleted books with restore functionality

### Changed
- `HomeScreen`: "Admin panel" button is visible only if `user.is_admin` is true

---

## v0.5.5 — Purchase history and balance top-up — 02/10/2026

### Added
- `gui/screens/history.py` — purchase history screen
- `gui/screens/top_up_dialog.py` — balance top-up modal dialog

### Changed
- `HomeScreen`: "Purchase history" and "Top up balance" buttons; `balance_label` is now a screen attribute

---

## v0.5.4 — Purchase — 30/09/2026

### Added
- `CatalogScreen`: book selection + quantity + "Buy selected" button
- Display and update of user balance in the catalog screen header

### Design note
The purchase result is displayed via an inline label rather than a `messagebox`; modal
dialogs hang during headless tests (without an actual click) and are inconsistent with
the rest of the UI (login, registration, and search errors were already displayed using labels).

---

## v0.5.3 — Catalog and search — 26/09/2026

### Added
- `gui/screens/catalog.py` — `Treeview` with book list, search, "Show all"

### Changed
- `HomeScreen`: "Browse catalog" button

## v0.5.2 — Auth screens — 25/09/2026

### Added
- `gui/screens/login.py`, `register.py`, `home.py`
- `BookstoreApp` now starts on `LoginScreen`

### Removed
- `gui/screens/placeholder.py` — served its purpose in v1.0; replaced by actual screens

---

## v0.5.1 — Hotfix: MySQL syntax & DB connection — 23/09/2026

### Fixed
- **Database Initialization**: Fixed SQL syntax error on older MySQL versions (< 8.0.19) by replacing `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` with standard `ALTER TABLE` and catching MySQL error `1060` (`ER_DUP_FIELDNAME`).
- **Database Connection**: Resolved `1049 (Unknown database)` error on startup by passing `database=MYSQL_DB_NAME` in connection parameters and removing manual `USE` queries from `gui_main.py`.
- **Import Sorting**: Fixed import order in `app/database.py` according to `ruff` linting rules (`I001`).

---

## v0.5.0 — GUI skeleton - 22/09/2026

### Added
- `bootstrap.py` — `build_services()`: unified repository/service assembly for CLI and GUI
- `gui/app.py` — `BookstoreApp`: root Tkinter window with screen switching
- `gui/screens/placeholder.py` — temporary confirmation screen
- `gui_main.py` — GUI entry point (`python -m bookstore_modules.gui_main`)

### Changed
- `main.py` updated to use `bootstrap.build_services()` instead of assembling repositories/services directly

---

## v0.4.6 — CI - 18/09/2026

### Added
- `.github/workflows/ci.yml` — GitHub Actions: linting (`ruff`), syntax check, and `pytest` with coverage on every `push`/`pull_request` to `main`
- `../pyproject.toml` — `ruff` configuration (`line-length = 120`, rules `E`, `F`, `I`)
- `requirements-dev.txt`: `ruff`, `pytest-cov`

### Changed
- Import sorting standardized across 11 files (`ruff --fix` autofix; import order only, no logic changes)

---

## v0.4.5 — Docker (MySQL + MongoDB) - 17/09/2026

### Added
- `../docker-compose.yml` — `mysql` and `mongodb` containers; data stored on disk at `D:\DB`
- `../docker` — creates MySQL users with read/edit permissions based on `.env` variables
- `../docker` — instructions for launching and working with local data storage
- `.env.example`: `MYSQL_ROOT_PASSWORD` and `MONGO_ROOT_PASSWORD`

---

## v0.4.4 — Comprehensive pytest suite - 16/09/2026

### Added
- `pytest.ini` and `requirements-dev.txt` — testing framework configuration and development dependencies
- `tests/conftest.py` — fake repository fixtures mimicking exact database rules (`deleted_at IS NULL`, stock validations)
- Unit tests for all domain services (`AuthService`, `PurchaseService`, `AdminService`, `CatalogService`)
- `test_money.py` — unit tests for `parse_money()` covering 2-decimal precision, `ROUND_HALF_UP` behavior, and invalid inputs
- Repository unit tests using `pymysql` mocks (`BookRepository`, `UserRepository`, `PurchaseRepository`) asserting exact SQL query strings and parameter bindings
- `test_user_repository.py` — password verification tests executing real `bcrypt` functions

### Fixed
- Verified purchase history durability against book soft deletion via explicit integration tests
- Guaranteed SQL query contracts via mock assertions to prevent regressions such as accidentally omitting `deleted_at IS NULL` filters

## v0.4.3 — Soft delete for books - 12/09/2026

### Added
- `books.deleted_at DATETIME NULL` — new column (with a migration for existing databases using `ADD COLUMN IF NOT EXISTS`)
- `BookRepository.get_deleted()` / `.restore()`
- `AdminService.list_deleted_books()` / `.restore_book()`
- "5. Restore deleted book" option in the admin panel

### Changed
- `BookRepository.delete()` now performs `UPDATE ... SET deleted_at = NOW()` instead of `DELETE FROM books`
- `get_all`, `search`, `get_by_id`, `decrease_stock`, `update`, and `upsert_by_title_author` — all filter by/account for `deleted_at IS NULL` so that deleted books do not interfere with catalog operations, while their records are preserved for purchase history

### Fixed
- Deleting a book no longer breaks past purchase history — the record remains in the table, and the `JOIN` in `PurchaseRepository.get_by_user` continues to retrieve the title, author, and price even for deleted books

---

## v0.4.2 — Logging - 10/09/2026

### Added
- `logging_config.py` — `bookstore` logger with file rotation (`LOG_FILE`/`LOG_LEVEL` from `.env`) and duplication of `WARNING+` level logs to the console
- `app/main.py` — top-level exception handling: unexpected exceptions are logged via `logger.exception()`, and a user-friendly message is displayed instead of a traceback

### Changed
- `database.py`, `services/search_logs.py`, `services/auth.py`, `services/purchase_service.py`, `services/admin_service.py` — events and errors (registration, login, purchases, top-ups, admin actions, connection failures) are now logged, replacing previous practices of either not recording them at all or outputting them via `print` statements within the business logic
- `services/purchase_service.py`: logging for failed purchases now covers the initial stock check (prior to the transaction start), not just failures occurring within the transaction itself

---

## v0.4.1 — Decimal for money - 09/09/2026

### Added
- `money.py` — `parse_money()`: parses monetary input into a `Decimal`, rounding to 2 decimal places using `ROUND_HALF_UP`

### Changed
- `models.py`: `Book.price`, `User.balance`, `Purchase.price`/`total` — now use `Decimal` instead of `float`
- All monetary input points (registration, topping up balance, adding/editing a book, importing from a file) now use `parse_money()` instead of `float()`
- `admin_service.import_from_file`: rows with invalid price/stock values are now skipped instead of causing the import to fail with an exception

### Fixed
- Resolved the risk of `TypeError` when mixing `Decimal` (values read from MySQL `DECIMAL` columns—pymysql returns them as `Decimal` by default) and `float` (user-entered values) in a single arithmetic expression

## v0.4.0 — OOP refactor - 08/09/2026

### Added
- `../app/models.py` — `Book`, `User`, and `Purchase` defined as dataclasses
- `../app/exceptions.py` — domain-specific exceptions (`UsernameTakenError`, `InsufficientStockError`, `BookNotFoundError`, etc.)
- `../app/services/catalog_service.py`, `../app/services/purchase_service.py`, `../app/services/admin_service.py` — business logic extracted from `../app/services/bookstore.py`
- `../app/user_interface/console_app.py`, `admin_menu.py`, `formatting.py`

### Changed
- `../app/db/books.py`, `../app/db/users.py`, `../app/db/purchases.py`, `../app/services/search_logs.py`, and `../app/services/auth.py` rewritten as repository/service classes; repositories now manage their own read/edit connections internally instead of requiring a connection to be passed manually with every call
- Services no longer contain `input()` or `print()` calls—only data and exceptions; all I/O is now handled in `../app/user_interface/`
- **Behavioral change:** "Load books from file" moved from the main menu (pre-login) to the admin panel—bulk database writes now require administrator privileges

### Removed
- `../app/services/bookstore.py`, `../app/user_interface/menu.py` (functionality distributed across new files)

---

## v0.3.1 — User Balance Top-Up - 06/09/2026

### Added
- User balance top-up functionality (`6. Top up balance` in the menu) via `top_up_balance()` service method
- Database functions `increase_balance()` and `get_balance()` in `app/db/users.py` to safely update and query user account funds

### Changed
- Shifted the "Admin panel" menu entry to `7. Admin panel` to accommodate the new top-up balance option

## v0.3.0 — Real search, purchase history, admin panel - 06/09/2026

### Added
- Real book search by title/author (`LIKE` query in `db.books.search_books`); search and logging happen simultaneously
- User purchase history (`5. Purchase history` in the menu) — JOIN `purchases` + `books`
- Admin panel: add, edit, and delete books. Access is determined by the `ADMIN_USERNAMES` list in `.env`, rather than a database flag or user self-assignment

### Changed
- `auth.login` now returns `(user_id, username)` — the username is required to verify admin access
- `user_menu` accepts `username` and displays the "Admin panel" option only for admins

---

## v0.2.0 — Security - 04/09/2026

### Added
- User password hashing (bcrypt) instead of plaintext storage
- User-friendly error handling for MySQL (`DatabaseConnectionError`) and MongoDB (`PyMongoError`) connection issues instead of raw tracebacks
- Validation for empty usernames/passwords during registration

### Changed
- `users.password`: `VARCHAR(100)` → `VARCHAR(255)` to accommodate bcrypt hashes

### Security
- Passwords are no longer compared directly within SQL queries (`WHERE password = %s`); verification is now performed at the application level using `bcrypt.checkpw`

---

## v0.1.0 — Project recovery - 03/09/2026

### Added
- Project structure restored following repository loss: `app/db/`, `app/services/`, `app/user_interface/`
- MySQL/MongoDB configuration via `.env` (`python-dotenv`), eliminating hardcoded credentials
- Separate read/edit MySQL connections at the code level
- `.env.example`, `.gitignore`, `requirements.txt`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`

### Security
- Initial repository commit contains no secrets
