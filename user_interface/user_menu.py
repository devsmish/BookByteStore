from services.bookstore import purchase_book
from services.search_logs import show_popular_queries, log_search
from db.books import get_all_books, view_books


def user_menu(read_connection, edit_connection, user_id):
    while True:
        print("\n--- User Menu ---")
        print("1. View books")
        print("2. Search books")
        print("3. Purchase")
        print("4. Popular searches")
        print("0. Logout")

        choice = input("Choice: ")

        if choice == "1":
            books_list = get_all_books(read_connection)
            view_books(books_list)

        elif choice == "2":
            query = input("Enter title: ")
            log_search(query)

        elif choice == "3":
            purchase_book(read_connection, edit_connection, user_id)

        elif choice == "4":
            show_popular_queries()

        elif choice == "0":
            return
