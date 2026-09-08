from app.models import Book


class BookRepository:
    def __init__(self, read_connection, edit_connection):
        self._read = read_connection
        self._edit = edit_connection

    def get_all(self):
        with self._read.cursor() as cursor:
            cursor.execute("SELECT * FROM books WHERE stock > 0")
            return [self._to_book(row) for row in cursor.fetchall()]

    def search(self, query, only_in_stock=True):
        sql = "SELECT * FROM books WHERE (title LIKE %s OR author LIKE %s)"
        if only_in_stock:
            sql += " AND stock > 0"
        like_query = f"%{query.strip()}%"
        with self._read.cursor() as cursor:
            cursor.execute(sql, (like_query, like_query))
            return [self._to_book(row) for row in cursor.fetchall()]

    def get_by_id(self, book_id):
        with self._read.cursor() as cursor:
            cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            row = cursor.fetchone()
            return self._to_book(row) if row else None

    def add(self, book):
        with self._edit.cursor() as cursor:
            cursor.execute("""
                INSERT INTO books (title, author, price, stock)
                VALUES (%s, %s, %s, %s)
            """, (book.title, book.author, book.price, book.stock))
        self._edit.commit()

    def update(self, book):
        with self._edit.cursor() as cursor:
            cursor.execute("""
                UPDATE books
                SET title = %s, author = %s, price = %s, stock = %s
                WHERE id = %s
            """, (book.title, book.author, book.price, book.stock, book.id))
            updated = cursor.rowcount
        self._edit.commit()
        return updated

    def delete(self, book_id):
        with self._edit.cursor() as cursor:
            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            deleted = cursor.rowcount
        self._edit.commit()
        return deleted

    def upsert_by_title_author(self, title, author, price, added_stock):
        """Used when importing from a file: increases stock if the book already exists."""
        with self._edit.cursor() as cursor:
            cursor.execute("""
                SELECT id, stock FROM books WHERE title = %s AND author = %s
            """, (title, author))
            result = cursor.fetchone()

            if result:
                book_id, current_stock = result
                cursor.execute("""
                    UPDATE books SET stock = %s WHERE id = %s
                """, (current_stock + added_stock, book_id))
            else:
                cursor.execute("""
                    INSERT INTO books (title, author, price, stock)
                    VALUES (%s, %s, %s, %s)
                """, (title, author, price, added_stock))

    def decrease_stock(self, book_id, quantity):
        """does not commit;
        it is called as part of the purchase transaction."""
        with self._edit.cursor() as cursor:
            cursor.execute("""
                UPDATE books
                SET stock = stock - %s
                WHERE id = %s AND stock >= %s
            """, (quantity, book_id, quantity))
            return cursor.rowcount

    def commit(self):
        self._edit.commit()

    @staticmethod
    def _to_book(row):
        book_id, title, author, price, stock = row
        return Book(id=book_id, title=title, author=author, price=price, stock=stock)
