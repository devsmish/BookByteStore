from app.exceptions import (
    BookstoreError,
    InvalidInputError,
    BookNotFoundError,
    InsufficientStockError,
    InsufficientBalanceError,
)
from app.logging_config import get_logger


logger = get_logger(__name__)

class PurchaseService:
    def __init__(self, book_repository, user_repository, purchase_repository, edit_connection):
        self._books = book_repository
        self._users = user_repository
        self._purchases = purchase_repository
        self._edit_connection = edit_connection

    def purchase(self, user_id, book_id, quantity):
        try:
            if quantity <= 0:
                raise InvalidInputError("Quantity must be positive")

            book = self._books.get_by_id(book_id)
            if not book:
                raise BookNotFoundError(book_id)
            if book.stock < quantity:
                raise InsufficientStockError(book.title)

            total = book.price * quantity

            if not self._books.decrease_stock(book_id, quantity):
                raise InsufficientStockError(book.title)
            if not self._users.decrease_balance(user_id, total):
                raise InsufficientBalanceError()
            self._purchases.add(user_id, book_id, quantity)
            self._edit_connection.commit()
        except BookstoreError as e:
            self._edit_connection.rollback()
            logger.warning("Purchase failed for user %s, book %s: %s", user_id, book_id, e)
            raise

        logger.info("User %s purchased %s x book %s (#%s) for %s", user_id, quantity, book.title, book_id, total)
        return total

    def history(self, user_id):
        return self._purchases.get_by_user(user_id)

    def top_up(self, user_id, amount):
        if amount <= 0:
            raise InvalidInputError("Amount must be positive")
        self._users.increase_balance(user_id, amount)
        logger.info("User %s topped up balance by %s", user_id, amount)
        return self._users.get_balance(user_id)
