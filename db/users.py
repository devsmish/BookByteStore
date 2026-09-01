def create_user(connection, username, password, balance):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False

        cursor.execute("""
            INSERT INTO users (username, password, balance)
            VALUES (%s, %s, %s)
        """, (username, password, balance))

    connection.commit()
    return True


def get_user(connection, username, password):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM users
            WHERE username = %s AND password = %s
        """, (username, password))
        return cursor.fetchone()


def decrease_balance(connection, user_id, amount):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE users
            SET balance = balance - %s
            WHERE id = %s AND balance >= %s
        """, (amount, user_id, amount))

        return cursor.rowcount
    