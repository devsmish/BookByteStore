# Roadmap

## v0.1 — Core (implemented in this build)
- DB/table initialization via edit connection
- Registration/login, book browsing, purchasing with transaction and rollback
- Loading books from a file
- Search query log and top 5 popular queries (MongoDB)
- **All credentials via `.env`; separation of read/edit MySQL connections**

## v0.2 — Reliability
- Password hashing (bcrypt) instead of plain text
- Connection error handling (clear messages instead of tracebacks when MySQL/Mongo are unavailable)
- Input validation (negative prices/quantities, etc.)
- Error logging using the `logging` module instead of `print`

## v0.3 — Features
- Actual book search by title/author (currently, `log_search` only logs the query but does not filter the list)
- Admin mode: manual addition/editing/deletion of books
- User purchase history (data is already being written to `purchases` but is not currently read anywhere)

## v0.3.1 — Balance
- Balance top-up

## v0.4 — Transition to OOP
- `../app/models.py`: `Book`, `User`, and `Purchase` implemented as dataclass models
- `../app/exceptions.py`: domain-specific exceptions used instead of `print` statements within business logic
- `../app/db/`: `BookRepository`, `UserRepository`, and `PurchaseRepository` — classes manage their own read/edit connections
- `../app/services/`: `AuthService`, `CatalogService`, `PurchaseService`, `AdminService`, and `SearchLogRepository` — business logic only; no `input()` or `print()` calls
- `../app/user_interface/`: `ConsoleApp`, `UserMenu`, and `AdminMenu` — all input/output handled here
- "Load books from file" moved from the main menu to the admin panel (requires administrator login)

## v0.4.1 — Using Decimal instead of float for monetary values
- [x] `money.py`: `parse_money()` — parses user input into `Decimal`, using `ROUND_HALF_UP` rounding to 2 decimal places (matching `DECIMAL(10,2)` in the schema)
- [x] `models.py`: `Book.price`, `User.balance`, `Purchase.price/total` — typed as `Decimal`
- [x] All 5 locations handling monetary input (`console_app._register`, `admin_menu._read_book_fields`×2, `user_menu._top_up`, `admin_service.import_from_file`) have been switched from `float()` to `parse_money()`
- [x] Also: invalid price/balance values in the import file are now silently skipped (similar to how lines of incorrect length were previously skipped) instead of causing the entire import to fail

## v0.4.2 — switched from `print` to `logging` for errors/events
- [x] `logging_config.py`: `bookstore` logger with file rotation (`LOG_FILE`, defaults to `bookstore.log`) + `WARNING+` output to console
- [x] `database.py`: connection errors logged before being wrapped in `DatabaseConnectionError`
- [x] `services/search_logs.py`: MongoDB errors logged as `WARNING`
- [x] `services/auth.py`: registration/login (success and failure) — `INFO`/`WARNING`, passwords excluded from logs
- [x] `services/purchase_service.py`: purchases and top-ups — `INFO`; failed purchases (including early stock checks, not just transaction failures) — `WARNING`
- [x] `services/admin_service.py`: adding/editing/deleting books, file imports — `INFO`
- [x] `app/main.py`: unhandled exceptions no longer crash the app with a raw traceback; logged via `logger.exception()`, user sees a clear message
- [x] `*.log` added to `.gitignore`

## v0.4.3 — Soft delete for books
- [x] `books.deleted_at DATETIME NULL` in schema + migration for existing databases (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`, MySQL ≥ 8.0.29 / MariaDB ≥ 10.0.2)
- [x] `BookRepository.delete()` — `UPDATE ... SET deleted_at = NOW()` instead of `DELETE`
- [x] All read queries (`get_all`, `search`, `get_by_id`, `decrease_stock`) filter by `deleted_at IS NULL` — deleted books are not visible in the catalog and cannot be purchased
- [x] `get_deleted()` / `restore()` in the repository, `list_deleted_books()` / `restore_book()` in `AdminService`, "5. Restore deleted book" option in the admin panel
- [x] Verified: purchase → soft delete → book hidden from catalog and unavailable for purchase → **purchase history remains intact** → restoration returns the book to the catalog

## v0.4.4 — Comprehensive pytest suite
- [x] `pytest.ini` & `requirements-dev.txt` configured
- [x] `tests/conftest.py`: fake repositories enforcing SQL semantics (`deleted_at IS NULL`, stock checks)
- [x] Service layer unit tests (`AuthService`, `PurchaseService`, `AdminService`, `CatalogService`)
- [x] `money.py` unit tests for `Decimal` conversion and rounding precision
- [x] Repository SQL contract tests (`BookRepository`, `UserRepository`, `PurchaseRepository`) using `pymysql` connection mocks
- [x] Real `bcrypt` hashing tests in `UserRepository`
- [x] Purchase history preservation integration test post soft delete

## v0.4.5 — Docker (MySQL + MongoDB)
- [x] `../docker-compose.yml`: контейнеры `mysql` (книги/пользователи/покупки) и `mongodb` (лог поисковых запросов), данные на диске в `D:\DB` (не в Docker volume)
- [x] Один `.env` управляет и приложением, и docker-compose (переменные `${VAR}` читаются из корневого `.env`) — не нужно дублировать пароли в двух местах
- [x] `../docker`: создаёт read/edit MySQL-пользователей с теми же кредами, что в `.env`, при первом запуске
- [x] `../docker` — инструкция по запуску, работе с `D:\DB`, пересозданию БД

## v0.4.6 — CI (done)
- [x] `.github/workflows/ci.yml`: on every `push`/`pull_request` to `main` — linting (`ruff`), syntax checks, and tests with coverage
- [x] `../pyproject.toml`: explicitly pinned `ruff` rule set (`E`, `F`, `I`) — intentionally restricted to prevent CI from accidentally adopting stricter defaults from a future version of the tool
- [x] Auto-fix for import sorting across the entire project (11 files; only `import` order changed, semantics remained the same)
- [x] CI does not require a running database — the entire test suite operates using fake repositories and mocks; no actual MySQL/MongoDB is needed

## v0.5 — Tkinter GUI
- `app/gui/` layer (already created as an empty package) — windows built on top of the existing `services` and `db` layers, without duplicating business logic
- Screens: login/registration → book catalog → purchase → history
- CLI (`user_interface`) remains as an alternative startup mode (`--cli`))

## v1.0 — Release
- Tests (`pytest`) for `db` and `services`
- CI (lint + tests)
- Packaging, final README/GUI screenshots
