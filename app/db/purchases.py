from app.models import Purchase


class PurchaseRepository:
    def __init__(self, read_connection, edit_connection):
        self._read = read_connection
        self._edit = edit_connection

    def add(self, user_id, book_id, quantity):
        """does not commit;
        it is called as part of the purchase transaction."""
        with self._edit.cursor() as cursor:
            cursor.execute("""
                INSERT INTO purchases (user_id, book_id, quantity, purchase_date)
                VALUES (%s, %s, %s, CURDATE())
            """, (user_id, book_id, quantity))

    def get_by_user(self, user_id):
        with self._read.cursor() as cursor:
            cursor.execute("""
                SELECT p.purchase_date, b.title, b.author, p.quantity, b.price,
                       (p.quantity * b.price) AS total
                FROM purchases p
                JOIN books b ON b.id = p.book_id
                WHERE p.user_id = %s
                ORDER BY p.purchase_date DESC, p.id DESC
            """, (user_id,))
            return [Purchase(*row) for row in cursor.fetchall()]
