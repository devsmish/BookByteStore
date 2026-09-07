from app.exceptions import BookstoreError
from app.user_interface.user_menu import UserMenu


class ConsoleApp:
    def __init__(self, auth_service, catalog_service, purchase_service, admin_service):
        self._auth = auth_service
        self._catalog = catalog_service
        self._purchase = purchase_service
        self._admin = admin_service

    def run(self):
        while True:
            print("\n==== Bookstore ====")
            print("1. Register")
            print("2. Login")
            print("0. Exit")

            choice = input("Choice: ")

            if choice == "1":
                self._register()
            elif choice == "2":
                self._login()
            elif choice == "0":
                break

    def _register(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        try:
            balance = float(input("Enter balance: "))
        except ValueError:
            print("Invalid balance")
            return

        try:
            self._auth.register(username, password, balance)
            print("Registration successful")
        except BookstoreError as e:
            print(f"Registration failed: {e}")

    def _login(self):
        username = input("Enter username: ")
        password = input("Enter password: ")

        try:
            user = self._auth.login(username, password)
        except BookstoreError as e:
            print(f"Login failed: {e}")
            return

        print("Login successful")
        UserMenu(self._catalog, self._purchase, self._admin, user).run()
