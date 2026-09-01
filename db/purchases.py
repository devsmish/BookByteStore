def add_purchase(connection, user_id, book_id, quantity):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO purchases (user_id, book_id, quantity, purchase_date)
            VALUES (%s, %s, %s, CURDATE())
        """, (user_id, book_id, quantity))
