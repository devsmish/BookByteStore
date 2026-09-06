from config import is_admin
from services.bookstore import (
    purchase_book,
    search_books,
    view_purchase_history,
    top_up_balance,
    admin_add_book,
    admin_update_book,
    admin_delete_book,
)
from services.search_logs import show_popular_queries
from db.books import get_all_books, view_books


def user_menu(read_connection, edit_connection, user_id, username):
    admin = is_admin(username)

    while True:
        print(f"\n--- User Menu ({username}) ---")
        print("1. View books")
        print("2. Search books")
        print("3. Purchase")
        print("4. Popular searches")
        print("5. Purchase history")
        print("6. Top up balance")
        if admin:
            print("7. Admin panel")
        print("0. Logout")

        choice = input("Choice: ")

        if choice == "1":
            books_list = get_all_books(read_connection)
            view_books(books_list)

        elif choice == "2":
            query = input("Enter title or author: ")
            search_books(read_connection, query)

        elif choice == "3":
            purchase_book(read_connection, edit_connection, user_id)

        elif choice == "4":
            show_popular_queries()

        elif choice == "5":
            view_purchase_history(read_connection, user_id)

        elif choice == "6":
            top_up_balance(edit_connection, user_id)

        elif choice == "7" and admin:
            admin_menu(edit_connection)

        elif choice == "0":
            return


def admin_menu(edit_connection):
    while True:
        print("\n--- Admin Panel ---")
        print("1. Add book")
        print("2. Edit book")
        print("3. Delete book")
        print("0. Back")

        choice = input("Choice: ")

        if choice == "1":
            admin_add_book(edit_connection)
        elif choice == "2":
            admin_update_book(edit_connection)
        elif choice == "3":
            admin_delete_book(edit_connection)
        elif choice == "0":
            return
