from services import auth
from services import bookstore
from user_interface.user_menu import user_menu

def main_menu(connection):
    while True:
        print("\n==== Bookstore ====")
        print("1. Load books from file")
        print("2. Register")
        print("3. Login")
        print("0. Exit")

        choice = input("Choice: ")

        if choice == "1":
            filename = input("Enter file name: ")
            bookstore.load_books_from_file(connection, filename)

        elif choice == "2":
            auth.register(connection)

        elif choice == "3":
            user_id = auth.login(connection)
            if user_id:
                user_menu(connection, user_id)

        elif choice == "0":
            break