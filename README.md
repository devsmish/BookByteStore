# BookByteStore

Bookstore console application: MySQL (books, users, purchases) + MongoDB (search query log). CLI serves as a temporary 
interface during the initial development phase; a Tkinter-based GUI is planned for the future.

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
├── database.py            # connection config (read/edit) from .env
├── main.py                # entry point
├── db/                    # low-level SQL queries
├── services/              # business logic (auth, purchases, book downloads, search logs)
├── user_interface/        # console menus
└── gui/                   # (plan) Tkinter-interface
```

## Configuration (.env)

Two MySQL connections:
- **read** — for SELECT operations only (viewing books, login)
- **edit** — for INSERT/UPDATE/CREATE (registration, purchase, book downloading, database initialization)

Plus `MONGO_URI` for the search query log.

## Format books.txt

```
Title,Author,Price,Stock
```

## Roadmap

See `../ROADMAP.md`.
