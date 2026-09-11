from app.exceptions import BookstoreError
from app.user_interface.formatting import print_books
from app.money import parse_money


class AdminMenu:
    def __init__(self, admin_service):
        self._admin = admin_service

    def run(self):
        while True:
            print("\n--- Admin Panel ---")
            print("1. Add book")
            print("2. Edit book")
            print("3. Delete book")
            print("4. Load books from file")
            print("5. Restore deleted book")
            print("0. Back")

            choice = input("Choice: ")

            if choice == "1":
                self._add_book()
            elif choice == "2":
                self._update_book()
            elif choice == "3":
                self._delete_book()
            elif choice == "4":
                self._import_from_file()
            elif choice == "5":
                self._restore_book()
            elif choice == "0":
                return

    def _read_book_fields(self, defaults=None):
        if defaults:
            title = input(f"Title [{defaults.title}]: ").strip() or defaults.title
            author = input(f"Author [{defaults.author}]: ").strip() or defaults.author
            price_input = input(f"Price [{defaults.price}]: ").strip()
            stock_input = input(f"Stock [{defaults.stock}]: ").strip()
            price = parse_money(price_input) if price_input else defaults.price
            stock = int(stock_input) if stock_input else defaults.stock
        else:
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            price = parse_money(input("Price: "))
            stock = int(input("Stock: "))
        return title, author, price, stock

    def _add_book(self):
        try:
            title, author, price, stock = self._read_book_fields()
            self._admin.add_book(title, author, price, stock)
            print("Book added.")
        except (BookstoreError, ValueError) as e:
            print(f"Could not add book: {e}")

    def _update_book(self):
        book_list = self._admin.list_books()
        print_books(book_list)
        if not book_list:
            return

        try:
            index = int(input("Enter book number to edit: ")) - 1
            if not (0 <= index < len(book_list)):
                print("Invalid book number.")
                return

            current = book_list[index]
            print("Leave a field empty to keep current value.")
            title, author, price, stock = self._read_book_fields(defaults=current)
            self._admin.update_book(current.id, title, author, price, stock)
            print("Book updated.")
        except (BookstoreError, ValueError) as e:
            print(f"Could not update book: {e}")

    def _delete_book(self):
        book_list = self._admin.list_books()
        print_books(book_list)
        if not book_list:
            return

        try:
            index = int(input("Enter book number to delete: ")) - 1
            if not (0 <= index < len(book_list)):
                print("Invalid book number.")
                return

            book = book_list[index]
            confirm = input(f"Delete '{book.title}'? (y/n): ").strip().lower()
            if confirm != "y":
                print("Cancelled.")
                return

            self._admin.delete_book(book.id)
            print("Book deleted.")
        except (BookstoreError, ValueError) as e:
            print(f"Could not delete book: {e}")

    def _import_from_file(self):
        filename = input("Enter file name: ").strip()
        try:
            added = self._admin.import_from_file(filename)
            print(f"{added} new books loaded.")
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except (BookstoreError, ValueError) as e:
            print(f"Could not import books: {e}")

    def _restore_book(self):
        deleted_books = self._admin.list_deleted_books()
        if not deleted_books:
            print("No deleted books.")
            return

        print("Deleted books:")
        for i, book in enumerate(deleted_books, 1):
            print(f"{i}. {book.title} by {book.author} (deleted at {book.deleted_at})")

        try:
            index = int(input("Enter book number to restore: ")) - 1
            if not (0 <= index < len(deleted_books)):
                print("Invalid book number.")
                return

            book = deleted_books[index]
            self._admin.restore_book(book.id)
            print("Book restored.")
        except (BookstoreError, ValueError) as e:
            print(f"Could not restore book: {e}")
