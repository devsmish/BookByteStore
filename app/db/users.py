import bcrypt

from app.limits import MAX_MONEY, MAX_PASSWORD_BYTES
from app.models import User


class UserRepository:
    def __init__(self, read_connection, edit_connection):
        self._read = read_connection
        self._edit = edit_connection

    def username_exists(self, username):
        with self._read.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            return cursor.fetchone() is not None

    def create(self, username, password, balance):
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        with self._edit.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, password, balance)
                VALUES (%s, %s, %s)
            """, (username, hashed_password.decode("utf-8"), balance))
            user_id = cursor.lastrowid
        self._edit.commit()
        return user_id


    def authenticate(self, username, password):
        with self._read.cursor() as cursor:
            cursor.execute("SELECT id, username, password, balance FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()

        if not row:
            return None

        user_id, db_username, stored_password, balance = row
        # bcrypt only uses the first 72 bytes: 4.x ignores the rest silently, 5.x raises ValueError.
        # Passing at most 72 bytes keeps accounts created with long passwords working on both.
        if not bcrypt.checkpw(password.encode("utf-8")[:MAX_PASSWORD_BYTES], stored_password.encode("utf-8")):
            return None

        return User(id=user_id, username=db_username, balance=balance)


    def decrease_balance(self, user_id, amount):
        """does not commit;
        it is called as part of the purchase transaction."""
        with self._edit.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET balance = balance - %s
                WHERE id = %s AND balance >= %s
            """, (amount, user_id, amount))
            return cursor.rowcount


    def increase_balance(self, user_id, amount):
        with self._edit.cursor() as cursor:
            # The limit is checked inside the UPDATE (atomically): returns 0 when the new balance would
            # not fit DECIMAL(10,2) instead of failing with a driver error (or clamping, without STRICT mode).
            cursor.execute("""
                UPDATE users
                SET balance = balance + %s
                WHERE id = %s AND balance + %s <= %s
            """, (amount, user_id, amount, MAX_MONEY))
            updated = cursor.rowcount
        self._edit.commit()
        return updated


    def get_balance(self, user_id):
        with self._read.cursor() as cursor:
            cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else None
