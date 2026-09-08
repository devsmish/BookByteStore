from app.exceptions import BookstoreError
from app.money import parse_money
from app.user_interface.admin_menu import AdminMenu
from app.user_interface.formatting import print_books


class UserMenu:
    def __init__(self, catalog_service, purchase_service, admin_service, user):
        self._catalog = catalog_service
        self._purchase = purchase_service
        self._admin_service = admin_service
        self._user = user

    def run(self):
        while True:
            print(f"\n--- User Menu ({self._user.username}) ---")
            print("1. View books")
            print("2. Search books")
            print("3. Purchase")
            print("4. Popular searches")
            print("5. Purchase history")
            print("6. Top up balance")
            if self._user.is_admin:
                print("7. Admin panel")
            print("0. Logout")

            choice = input("Choice: ")

            if choice == "1":
                print_books(self._catalog.list_books())
            elif choice == "2":
                self._search()
            elif choice == "3":
                self._purchase_book()
            elif choice == "4":
                self._popular_queries()
            elif choice == "5":
                self._purchase_history()
            elif choice == "6":
                self._top_up()
            elif choice == "7" and self._user.is_admin:
                AdminMenu(self._admin_service).run()
            elif choice == "0":
                return

    def _search(self):
        query = input("Enter title or author: ")
        try:
            results, log_warning = self._catalog.search(query)
        except BookstoreError as e:
            print(f"Search failed: {e}")
            return

        if log_warning:
            print(f"(Note: search was not logged — {log_warning})")
        print_books(results)

    def _popular_queries(self):
        try:
            top = self._catalog.popular_queries()
        except BookstoreError as e:
            print(f"Popular searches unavailable: {e}")
            return

        if not top:
            print("No search data found.")
            return

        print("Most frequent search queries:")
        for i, (query, count) in enumerate(top, 1):
            print(f"{i}. {query} — {count} times")

    def _purchase_book(self):
        book_list = self._catalog.list_books()
        print_books(book_list)
        if not book_list:
            return

        try:
            index = int(input("Enter book number: ")) - 1
            quantity = int(input("Enter quantity: "))
        except ValueError:
            print("Invalid input.")
            return

        if not (0 <= index < len(book_list)):
            print("Invalid book number.")
            return

        book = book_list[index]
        try:
            total = self._purchase.purchase(self._user.id, book.id, quantity)
            print(f"Purchase successful. Total: ${total}")
        except BookstoreError as e:
            print(f"Purchase failed: {e}")

    def _purchase_history(self):
        history = self._purchase.history(self._user.id)
        if not history:
            print("No purchases yet.")
            return

        print("Your purchase history:")
        for p in history:
            print(f"{p.purchase_date} — {p.title} by {p.author}: {p.quantity} x ${p.price} = ${p.total}")

    def _top_up(self):
        try:
            amount = parse_money(input("Enter top-up amount: "))
            new_balance = self._purchase.top_up(self._user.id, amount)
            print(f"Balance topped up. Current balance: ${new_balance}")
        except (BookstoreError, ValueError) as e:
            print(f"Top-up failed: {e}")
