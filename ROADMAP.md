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

## v0.4 — Transition to OOP (complete)
- `../app/models.py`: `Book`, `User`, and `Purchase` implemented as dataclass models
- `../app/exceptions.py`: domain-specific exceptions used instead of `print` statements within business logic
- `../app/db/`: `BookRepository`, `UserRepository`, and `PurchaseRepository` — classes manage their own read/edit connections
- `../app/services/`: `AuthService`, `CatalogService`, `PurchaseService`, `AdminService`, and `SearchLogRepository` — business logic only; no `input()` or `print()` calls
- `../app/user_interface/`: `ConsoleApp`, `UserMenu`, and `AdminMenu` — all input/output handled here
- "Load books from file" moved from the main menu to the admin panel (requires administrator login)

## v0.5 — Tkinter GUI
- `app/gui/` layer (already created as an empty package) — windows built on top of the existing `services` and `db` layers, without duplicating business logic
- Screens: login/registration → book catalog → purchase → history
- CLI (`user_interface`) remains as an alternative startup mode (`--cli`))

## v1.0 — Release
- Tests (`pytest`) for `db` and `services`
- CI (lint + tests)
- Packaging, final README/GUI screenshots
