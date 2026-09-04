from database import (
    get_read_connection,
    get_edit_connection,
    init_db,
    db_name,
    DatabaseConnectionError,
)
from user_interface.menu import main_menu


def main():
    try:
        init_db()

        with get_read_connection() as read_connection, get_edit_connection() as edit_connection:
            with read_connection.cursor() as cursor:
                cursor.execute(f"USE {db_name}")
            with edit_connection.cursor() as cursor:
                cursor.execute(f"USE {db_name}")

            main_menu(read_connection, edit_connection)

    except DatabaseConnectionError as e:
        print(f"Database connection error: {e}")


if __name__ == "__main__":
    main()
