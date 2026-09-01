def get_all_books(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM books WHERE stock > 0")
        return cursor.fetchall()

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
    