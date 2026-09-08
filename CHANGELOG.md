# Changelog

## v0.4 — OOP refactor - 08/09/2026

### Added
- `../app/models.py` — `Book`, `User`, `Purchase` как dataclasses
- `../app/exceptions.py` — доменные исключения (`UsernameTakenError`, `InsufficientStockError`, `BookNotFoundError` и др.)
- `../app/services/catalog_service.py`, `../app/services/purchase_service.py`, `../app/services/admin_service.py` — бизнес-логика, вынесенная из `../app/services/bookstore.py`
- `../app/user_interface/console_app.py`, `admin_menu.py`, `formatting.py`

### Changed
- `../app/db/books.py`, `../app/db/users.py`, `../app/db/purchases.py`, `../app/services/search_logs.py`, `../app/services/auth.py` переписаны как классы-репозитории/сервисы; репозитории сами хранят read/edit-подключения вместо передачи нужного соединения вручную в каждом вызове
- Сервисы больше не содержат `input()`/`print()` — только данные и исключения; весь ввод-вывод теперь в `../app/user_interface/`
- **Поведенческое изменение:** "Load books from file" перенесён из главного меню (без логина) в админ-панель — массовая запись в БД теперь требует прав администратора

### Removed
- `../app/services/bookstore.py`, `../app/user_interface/menu.py` (функциональность распределена по новым файлам)

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
