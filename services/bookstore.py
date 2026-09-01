from database import db_name
from db import books, users, purchases


def load_books_from_file(connection, filename):
    added = 0
    with open(filename, encoding='utf-8') as file:
        with connection.cursor() as cursor:
            cursor.execute(f"USE {db_name}")
            for line in file:
                parts = line.strip().split(",")
                if len(parts) != 4:
                    continue  # skips invalid lines
                title, author, price, stock = parts
                price = float(price)
                stock = int(stock)

                # Checking book availability
                cursor.execute("""
                    SELECT id, stock FROM books
                    WHERE title = %s AND author = %s
                """, (title, author))
                result = cursor.fetchone()

                if result:
                    book_id, current_stock = result
                    cursor.execute("""
                        UPDATE books SET stock = %s WHERE id = %s
                    """, (current_stock + stock, book_id))
                else:
                    cursor.execute("""
                        INSERT INTO books (title, author, price, stock)
                        VALUES (%s, %s, %s, %s)
                    """, (title, author, price, stock))
                added += stock
    connection.commit()
    print(f"{added} new books loaded.")


def purchase_book(connection, user_id):
    book_list = books.get_all_books(connection)

    if not book_list:
        print("No books available.")
        return

    for i, (book_id, title, author, price, stock) in enumerate(book_list, 1):
        print(f"{i}. {title} by {author} - ${price} ({stock})")

    try:
        index = int(input("Enter book number: ")) - 1
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Invalid input.")
        return

    if not (0 <= index < len(book_list)):
        print("Invalid book number.")
        return

    book_id, _, _, price, stock = book_list[index]

    if quantity > stock:
        print("Not enough books in stock.")
        return

    total_price = price * quantity

    try:
        stock_updated = books.decrease_stock(connection, book_id, quantity)
        balance_updated = users.decrease_balance(connection, user_id, total_price)

        if not stock_updated:
            raise Exception("Stock error")

        if not balance_updated:
            raise Exception("Balance error")

        purchases.add_purchase(connection, user_id, book_id, quantity)

        connection.commit()
        print("Purchase successful.")

    except Exception:
        connection.rollback()
        print("Transaction failed.")
