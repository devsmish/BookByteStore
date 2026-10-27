# BookByteStore

Bookstore console application: MySQL (books, users, purchases) + MongoDB (search query log). CLI serves as a temporary 
interface during the initial development phase; a Tkinter-based GUI is planned for the future.

## Prerequisites & Database Requirements

- Python 3.10+
- **MySQL 5.7+** or **MariaDB** (compatible with older syntax via safe migration checks)
- MongoDB (for search query logging)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Database via Docker (recommended for local development)

```bash
docker compose up -d
```

Starts MySQL (books/users/purchases) and MongoDB (search query logs) with data stored on disk at `D:\DB`. See `../docker` for details.
The `.env.example` file already contains credentials matching this compose file.

Without Docker: connect your own MySQL/MongoDB instances and fill in `.env` manually.

## Launch

```bash
python -m app.main
```

Upon the first launch, `init_db()` will create the database and tables (`books`, `users`, `purchases`) using the edit 
connection.

### GUI (under development)

```bash
python -m app.gui_main
```

On Linux, you may need to install the system package for Tkinter bindings separately
from `pip` (e.g., `sudo apt install python3-tk` on Debian/Ubuntu); it is not
included in `requirements.txt` because `tkinter` is not installed via `pip`.
On Windows/macOS, it is usually included in the standard Python installation.

### Building an executable (Windows)

```bash
pip install -r requirements-build.txt
python build_scripts/build.py
```

Produces a single `dist/BookByteStore.exe`; put a filled-in `.env` next to it. Details, including what was
verified and what the exe does not make safer: `../build_scripts/README.md`.

## Structure

```
BookByteStore/
├── pytest.ini                 # pytest suite configuration
├── bookstore.spec             # PyInstaller recipe: single-file GUI executable
├── build_scripts/             # build.py + README: building the executable
├── requirements-build.txt     # PyInstaller, on top of requirements.txt
    app/
    ├── database.py            # connection config (read/edit) from .env, connection error logging & DB initialization/migrations
    ├── config.py               # list of admins (ADMIN_USERNAMES) from .env
    ├── env.py                   # where .env and the default log file live (next to the exe in a packaged build)
    ├── logging_config.py        # centralized logger configuration (file rotation + console handler)
    ├── main.py                    # entry point, assembling repositories/services & global exception handling
    ├── money.py                 # parse_money() utility for Decimal conversion & ROUND_HALF_UP rounding
    ├── limits.py                # limits mirroring the DB schema (DECIMAL(10,2), INT, VARCHAR sizes, bcrypt 72 bytes)
    ├── models.py                # domain models: Book (with deleted_at), User, Purchase (Decimal for monetary attributes)
    ├── exceptions.py             # domain exceptions
    ├── bootstrap.py               # Services: building repositories/services for CLI and GUI
    ├── gui_main.py                 # GUI entry point
    ├── db/                          # repositories — MySQL operations
    │   ├── books.py                  # BookRepository (catalog queries with soft-delete filtering, soft-delete & restore operations)
    │   ├── users.py                   # UserRepository (authenticated user lookup with 5-column tuple unpacking)
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
    ├─  gui/                                     # Tkinter interface
    │   ├── app.py                               # BookstoreApp: root window, screen switching controller
    │   ├── dialogs.py                           # Messagebox: confirm
    │   ├── style.py                             # constants PAD and apply style
    │   └── screens/                             # Application screens
    │       ├── admin.py                         # AdminScreen
    │       ├── login.py                         # LoginScreen
    │       ├── register.py                      # RegisterScreen
    │       ├── home.py                          # HomeScreen
    │       ├── history.py                       # HistoryScreen
    │       ├── top_up_dialog.py                 # TopUpDialog
    │       ├── book_form_dialog.py              # BookFormDialog
    │       ├── deleted_books.py                 # DeletedBooksScreen
    │       └── catalog.py                       # CatalogScreen (ttk.Treeview, search, non-blocking warning label, inline book purchasing & dynamic balance/stock updates)
    tests/                                             # pytest suite
    ├── conftest.py                                    # fake repository fixtures mirroring SQL semantics
    ├── test_auth_service.py                           # AuthService tests
    ├── test_purchase_service.py                       # PurchaseService & soft-delete history tests
    ├── test_admin_service.py                          # AdminService tests
    ├── test_catalog_service.py                        # CatalogService tests
    ├── test_money.py                                  # parse_money() precision & rounding tests
    ├── test_book_repository.py                        # BookRepository SQL contract tests
    ├── test_user_repository.py                        # UserRepository & real bcrypt tests
    ├── test_database.py                               # how connections are opened (autocommit read conn, FOUND_ROWS, DB name checks)
    ├── test_gui_robustness.py                         # unhandled Tk callback errors are logged and shown (needs a display; skipped otherwise)
    ├── test_purchase_repository.py                    # PurchaseRepository SQL contract tests
    ├── test_env.py                                    # .env / default log path do not depend on the working directory
    ├── test_packaging.py                              # guards for the PyInstaller setup (spec entry point, .gitignore)
    └── integration/                                   # real-MySQL tests (opt-in, see "Running Tests")
        ├── integration/                                   # real-MySQL tests (opt-in, see "Running Tests")
        ├── conftest.py                                    # real MySQL connection/DB fixtures & BBS_TEST_DB_* safeguards
        ├── test_stale_reads.py                            # read isolation & cross-connection balance visibility tests
        ├── test_rowcount_semantics.py                     # PyMySQL CLIENT.FOUND_ROWS matched vs affected row tests
        └── test_transactions_and_limits.py                # explicit rollback safety & DECIMAL/schema boundary tests
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

## Running Tests
```bash
pip install -r requirements.txt
pytest
pytest --cov=app --cov-report=term-missing  # coated
ruff check app tests                        # linter
```

Coverage: `services/` and `db/` repositories (63 tests: unit tests using fake repositories + repository 
tests using `pymysql` connection mocks that verify the actual SQL).

### Integration tests (real MySQL)

The unit tests use mocked connections, so they cannot see transaction/isolation behaviour or driver
semantics (e.g. stale reads on a long-lived connection, `cursor.rowcount`). `tests/integration` runs the
real application code against a real MySQL server.

> **They `DROP` and re-create a database.** For safety they never read `.env`, run only when the
> dedicated `BBS_TEST_DB_*` variables are set, and refuse a database whose name does not contain `test`.
> Never point them at your real database.

```bash
# Linux/macOS
BBS_TEST_DB_HOST=127.0.0.1 BBS_TEST_DB_USER=root BBS_TEST_DB_PASSWORD=secret \
BBS_TEST_DB_NAME=bookstore_itest pytest tests/integration -v
```

```powershell
# Windows PowerShell
$env:BBS_TEST_DB_HOST="127.0.0.1"; $env:BBS_TEST_DB_USER="root"; $env:BBS_TEST_DB_PASSWORD="secret"
$env:BBS_TEST_DB_NAME="bookstore_itest"; pytest tests/integration -v
```

Without these variables the integration tests are simply skipped, so plain `pytest` keeps working.
In CI they run in a separate `integration` job against a MySQL 8.0 service container.

## Roadmap

See `../ROADMAP.md`.
