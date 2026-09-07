import bcrypt

from models import User


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
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()

        if not row:
            return None

        user_id, db_username, stored_password, balance = row
        if not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
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
            cursor.execute("""
                UPDATE users
                SET balance = balance + %s
                WHERE id = %s
            """, (amount, user_id))
            updated = cursor.rowcount
        self._edit.commit()
        return updated


    def get_balance(self, user_id):
        with self._read.cursor() as cursor:
            cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else None
