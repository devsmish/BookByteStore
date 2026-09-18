from app.database import (
    DatabaseConnectionError,
    db_name,
    get_edit_connection,
    get_read_connection,
    init_db,
)
from app.db.books import BookRepository
from app.db.purchases import PurchaseRepository
from app.db.users import UserRepository
from app.logging_config import get_logger, setup_logging
from app.services.admin_service import AdminService
from app.services.auth import AuthService
from app.services.catalog_service import CatalogService
from app.services.purchase_service import PurchaseService
from app.services.search_logs import SearchLogRepository
from app.user_interface.console_app import ConsoleApp

logger = get_logger(__name__)

def main():
    setup_logging()
    logger.info("Application starting")

    try:
        init_db()

        with get_read_connection() as read_connection, get_edit_connection() as edit_connection:
            with read_connection.cursor() as cursor:
                cursor.execute(f"USE {db_name}")
            with edit_connection.cursor() as cursor:
                cursor.execute(f"USE {db_name}")

            book_repository = BookRepository(read_connection, edit_connection)
            user_repository = UserRepository(read_connection, edit_connection)
            purchase_repository = PurchaseRepository(read_connection, edit_connection)
            search_log_repository = SearchLogRepository()

            auth_service = AuthService(user_repository)
            catalog_service = CatalogService(book_repository, search_log_repository)
            purchase_service = PurchaseService(
                book_repository, user_repository, purchase_repository, edit_connection
            )
            admin_service = AdminService(book_repository)

            app = ConsoleApp(
                auth_service, catalog_service, purchase_service, admin_service
            )
            app.run()

    except DatabaseConnectionError as e:
        logger.error("Startup failed: %s", e)
        print(f"Database connection error: {e}")
    except Exception:
        logger.exception("Unexpected error")
        print("An unexpected error occurred. Details have been recorded in the log.")
    finally:
        logger.info("Application stopped")


if __name__ == "__main__":
    main()
