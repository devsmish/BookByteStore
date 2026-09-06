def add_purchase(connection, user_id, book_id, quantity):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO purchases (user_id, book_id, quantity, purchase_date)
            VALUES (%s, %s, %s, CURDATE())
        """, (user_id, book_id, quantity))

def get_user_purchases(connection, user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.purchase_date, b.title, b.author, p.quantity, b.price,
                   (p.quantity * b.price) AS total
            FROM purchases p
            JOIN books b ON b.id = p.book_id
            WHERE p.user_id = %s
            ORDER BY p.purchase_date DESC, p.id DESC
        """, (user_id,))
        return cursor.fetchall()
