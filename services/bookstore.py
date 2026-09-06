from database import db_name
from db import books, users, purchases
from services.search_logs import log_search


def search_books(read_connection, query):
    log_search(query)

    if not query.strip():
        print("Search query cannot be empty.")
        return

    results = books.search_books(read_connection, query)
    books.view_books(results)


def view_purchase_history(read_connection, user_id):
    history = purchases.get_user_purchases(read_connection, user_id)

    if not history:
        print("No purchases yet.")
        return

    print("Your purchase history:")
    for purchase_date, title, author, quantity, price, total in history:
        print(f"{purchase_date} — {title} by {author}: {quantity} x ${price} = ${total}")


def top_up_balance(edit_connection, user_id):
    try:
        amount = float(input("Enter top-up amount: "))
        if amount <= 0:
            raise ValueError
    except ValueError:
        print("Invalid amount.")
        return

    users.increase_balance(edit_connection, user_id, amount)
    new_balance = users.get_balance(edit_connection, user_id)
    print(f"Balance topped up. Current balance: ${new_balance}")


def _read_book_input():
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    try:
        price = float(input("Price: "))
        stock = int(input("Stock: "))
        if price < 0 or stock < 0:
            raise ValueError
    except ValueError:
        print("Invalid price or stock.")
        return None
    if not title or not author:
        print("Title and author cannot be empty.")
        return None
    return title, author, price, stock


def admin_add_book(edit_connection):
    parsed = _read_book_input()
    if not parsed:
        return
    title, author, price, stock = parsed
    books.add_book(edit_connection, title, author, price, stock)
    print("Book added.")


def admin_update_book(edit_connection):
    book_list = books.get_all_books(edit_connection)
    if not book_list:
        print("No books available.")
        return
    books.view_books(book_list)

    try:
        index = int(input("Enter book number to edit: ")) - 1
    except ValueError:
        print("Invalid input.")
        return
    if not (0 <= index < len(book_list)):
        print("Invalid book number.")
        return

    book_id = book_list[index][0]
    print("Leave a field empty to keep current value.")
    current = books.get_book_by_id(edit_connection, book_id)
    _, cur_title, cur_author, cur_price, cur_stock = current

    title = input(f"Title [{cur_title}]: ").strip() or cur_title
    author = input(f"Author [{cur_author}]: ").strip() or cur_author

    price_input = input(f"Price [{cur_price}]: ").strip()
    stock_input = input(f"Stock [{cur_stock}]: ").strip()

    try:
        price = float(price_input) if price_input else float(cur_price)
        stock = int(stock_input) if stock_input else cur_stock
        if price < 0 or stock < 0:
            raise ValueError
    except ValueError:
        print("Invalid price or stock.")
        return

    books.update_book(edit_connection, book_id, title, author, price, stock)
    print("Book updated.")


def admin_delete_book(edit_connection):
    book_list = books.get_all_books(edit_connection)
    if not book_list:
        print("No books available.")
        return
    books.view_books(book_list)

    try:
        index = int(input("Enter book number to delete: ")) - 1
    except ValueError:
        print("Invalid input.")
        return
    if not (0 <= index < len(book_list)):
        print("Invalid book number.")
        return

    book_id, title, *_ = book_list[index]
    confirm = input(f"Delete '{title}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    books.delete_book(edit_connection, book_id)
    print("Book deleted.")


def load_books_from_file(edit_connection, filename):
    added = 0
    with open(filename, encoding='utf-8') as file:
        with edit_connection.cursor() as cursor:
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
    edit_connection.commit()
    print(f"{added} new books loaded.")


def purchase_book(read_connection, edit_connection, user_id):
    book_list = books.get_all_books(read_connection)

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
        # Atomicity via conditions in UPDATE + a single transaction for edit_connection.
        stock_updated = books.decrease_stock(edit_connection, book_id, quantity)
        balance_updated = users.decrease_balance(edit_connection, user_id, total_price)

        if not stock_updated:
            raise Exception("Stock error")

        if not balance_updated:
            raise Exception("Balance error")

        purchases.add_purchase(edit_connection, user_id, book_id, quantity)

        edit_connection.commit()
        print("Purchase successful.")

    except Exception:
        edit_connection.rollback()
        print("Transaction failed.")
