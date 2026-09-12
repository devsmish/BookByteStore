# Changelog

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
- `main.py` — top-level exception handling: unexpected exceptions are logged via `logger.exception()`, and a user-friendly message is displayed instead of a traceback

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
