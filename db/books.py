def get_all_books(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM books WHERE stock > 0")
        return cursor.fetchall()

def search_books(connection, query, only_in_stock=True):
    sql = "SELECT * FROM books WHERE (title LIKE %s OR author LIKE %s)"
    if only_in_stock:
        sql += " AND stock > 0"
    like_query = f"%{query.strip()}%"
    with connection.cursor() as cursor:
        cursor.execute(sql, (like_query, like_query))
        return cursor.fetchall()

def get_book_by_id(connection, book_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        return cursor.fetchone()

def add_book(connection, title, author, price, stock):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO books (title, author, price, stock)
            VALUES (%s, %s, %s, %s)
        """, (title, author, price, stock))
    connection.commit()

def update_book(connection, book_id, title, author, price, stock):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE books
            SET title = %s, author = %s, price = %s, stock = %s
            WHERE id = %s
        """, (title, author, price, stock, book_id))
        updated = cursor.rowcount
    connection.commit()
    return updated

def delete_book(connection, book_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        deleted = cursor.rowcount
    connection.commit()
    return deleted

def view_books(books):
    if not books:
        print("No books available")
        return
    print("Available books: ")
    enumerated_books = dict(enumerate(books, 1))
    for order, (_, title, author, price, stock) in enumerated_books.items():
        print(f"{order}: {title} by {author} - ${price} ({stock} in stock)")

def decrease_stock(connection, book_id, quantity):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE books
            SET stock = stock - %s
            WHERE id = %s AND stock >= %s
        """, (quantity, book_id, quantity))

        return cursor.rowcount
