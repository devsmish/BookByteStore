from services import auth
from services import bookstore
from user_interface import user_menu


def main_menu(read_connection, edit_connection):
    while True:
        print("\n==== Bookstore ====")
        print("1. Load books from file")
        print("2. Register")
        print("3. Login")
        print("0. Exit")

        choice = input("Choice: ")

        if choice == "1":
            filename = input("Enter file name: ")
            bookstore.load_books_from_file(edit_connection, filename)

        elif choice == "2":
            auth.register(edit_connection)

        elif choice == "3":
            user_id = auth.login(read_connection)
            if user_id:
                user_menu(read_connection, edit_connection, user_id)

        elif choice == "0":
            break
