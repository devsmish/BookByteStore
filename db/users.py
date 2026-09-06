import bcrypt


def create_user(connection, username, password, balance):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO users (username, password, balance)
            VALUES (%s, %s, %s)
        """, (username, hashed_password.decode("utf-8"), balance))

    connection.commit()
    return True


def get_user(connection, username, password):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM users
            WHERE username = %s
        """, (username,))
        user = cursor.fetchone()

    if not user:
        return None

    stored_password = user[2]  # id, username, password, balance
    if not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
        return None

    return user


def decrease_balance(connection, user_id, amount):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE users
            SET balance = balance - %s
            WHERE id = %s AND balance >= %s
        """, (amount, user_id, amount))

        return cursor.rowcount


def increase_balance(connection, user_id, amount):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE users
            SET balance = balance + %s
            WHERE id = %s
        """, (amount, user_id))
        updated = cursor.rowcount
    connection.commit()
    return updated


def get_balance(connection, user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else None
