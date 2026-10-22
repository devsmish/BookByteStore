"""Limits that mirror the database schema (see ``init_db`` in app/database.py).

Validating against them in Python gives the user a clear message instead of a raw
driver error - and, on servers running without STRICT SQL mode, prevents values from
being silently truncated/clamped by MySQL.
"""
from decimal import Decimal

MAX_MONEY = Decimal("99999999.99")  # DECIMAL(10,2)
MAX_INT = 2_147_483_647             # INT (books.stock)
MAX_TITLE_LEN = 200                 # books.title    VARCHAR(200)
MAX_AUTHOR_LEN = 100                # books.author   VARCHAR(100)
MAX_USERNAME_LEN = 100              # users.username VARCHAR(100)
MAX_PASSWORD_BYTES = 72             # bcrypt only uses the first 72 bytes of a password
