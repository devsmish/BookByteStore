from app.exceptions import (
    BookNotFoundError,
    BookstoreError,
    InsufficientBalanceError,
    InsufficientStockError,
    InvalidInputError,
)
from app.limits import MAX_MONEY
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
            self._rollback()
            logger.warning("Purchase failed for user %s, book %s: %s", user_id, book_id, e)
            raise
        except Exception:
            # Not a domain error (lock timeout, lost connection, ...). The half-finished purchase must
            # still be rolled back: it would otherwise stay pending on the shared edit connection and be
            # committed by the next unrelated write - money and stock gone, no purchase record.
            self._rollback()
            logger.exception("Purchase failed unexpectedly for user %s, book %s", user_id, book_id)
            raise

        logger.info("User %s purchased %s x book %s (#%s) for %s", user_id, quantity, book.title, book_id, total)
        return total

    def _rollback(self):
        try:
            self._edit_connection.rollback()
        except Exception:
            logger.exception("Rollback failed")

    def history(self, user_id):
        return self._purchases.get_by_user(user_id)

    def top_up(self, user_id, amount):
        if amount <= 0:
            raise InvalidInputError("Amount must be positive")
        if not self._users.increase_balance(user_id, amount):
            raise InvalidInputError(f"Top-up would exceed the maximum balance ({MAX_MONEY})")
        logger.info("User %s topped up balance by %s", user_id, amount)
        return self._users.get_balance(user_id)
