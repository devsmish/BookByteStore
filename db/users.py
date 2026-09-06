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

    stored_password = user[2]
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
