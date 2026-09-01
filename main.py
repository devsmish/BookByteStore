from database import get_connection, init_db, db_name
from user_interface.menu import main_menu

def main():
    init_db()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"USE {db_name}")

        main_menu(connection)

if __name__ == "__main__":
    main()
