# BookByteStore

Bookstore console application: MySQL (books, users, purchases) + MongoDB (search query log). CLI serves as a temporary 
interface during the initial development phase; a Tkinter-based GUI is planned for the future.

## Prerequisites & Database Requirements

- Python 3.10+
- **MySQL ≥ 8.0.29** or **MariaDB ≥ 10.0.2** (required for `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` schema migrations)
- MongoDB (for search query logging)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Launch

```bash
python -m main
```

Upon the first launch, `init_db()` will create the database and tables (`books`, `users`, `purchases`) using the edit 
connection.

## Structure

```
BookByteStore/
├── main.py                    # entry point, assembling repositories/services & global exception handling
    app/
    ├── database.py            # connection config (read/edit) from .env, connection error logging & DB initialization/migrations
    ├── config.py               # list of admins (ADMIN_USERNAMES) from .env
    ├── logging_config.py        # centralized logger configuration (file rotation + console handler)
    ├── money.py                 # parse_money() utility for Decimal conversion & ROUND_HALF_UP rounding
    ├── models.py                # domain models: Book (with deleted_at), User, Purchase (Decimal for monetary attributes)
    ├── exceptions.py             # domain exceptions
    ├── db/                          # repositories — MySQL operations
    │   ├── books.py                  # BookRepository (catalog queries with soft-delete filtering, soft-delete & restore operations)
    │   ├── users.py                   # UserRepository
    │   └── purchases.py                # PurchaseRepository (JOIN queries preserved for soft-deleted books)
    ├── services/                        # business logic (no input()/print(), error & event logging)
    │   ├── auth.py                       # AuthService (registration, login)
    │   ├── catalog_service.py             # CatalogService (browsing, searching)
    │   ├── purchase_service.py             # PurchaseService (purchasing, history, balance top-up)
    │   ├── admin_service.py                 # AdminService (book CRUD, file import, soft-delete management & restoration)
    │   └── search_logs.py                    # SearchLogRepository (MongoDB logs)
    ├── user_interface/                         # console UI — all input()/print() here
    │   ├── console_app.py                        # ConsoleApp: registration/login
    │   ├── user_menu.py                           # UserMenu
    │   ├── admin_menu.py                           # AdminMenu (includes option to view & restore deleted books)
    │   └── formatting.py                            # shared output functions
    └── gui/                                          # (planned) Tkinter interface
```

## Configuration (.env)

Two MySQL connections:
- **read** — for SELECT operations only (viewing books, login)
- **edit** — for INSERT/UPDATE/CREATE (registration, purchase, book downloading, database initialization)

MongoDB:

- **MONGO_URI** — for the search query log.

Logging:

- **LOG_FILE** — path to the application log file (defaults to bookstore.log, rotated at 1 MB with 3 backups)

- **LOG_LEVEL** — application logging level (INFO, WARNING, ERROR, etc.)

## Format books.txt

```
Title,Author,Price,Stock
```

## Roadmap

See `../ROADMAP.md`.
