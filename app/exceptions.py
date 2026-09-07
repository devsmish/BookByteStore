class BookstoreError(Exception):
    """Base exception for all project domain errors."""


class InvalidInputError(BookstoreError):
    """Invalid data entered by the user."""


class UsernameTakenError(BookstoreError):
    def __init__(self, username):
        super().__init__(f"Username '{username}' is already taken")
        self.username = username


class InvalidCredentialsError(BookstoreError):
    def __init__(self):
        super().__init__("Invalid username or password")


class BookNotFoundError(BookstoreError):
    def __init__(self, book_id):
        super().__init__(f"Book #{book_id} not found")
        self.book_id = book_id


class InsufficientStockError(BookstoreError):
    def __init__(self, title):
        super().__init__(f"Not enough stock for '{title}'")
        self.title = title


class InsufficientBalanceError(BookstoreError):
    def __init__(self):
        super().__init__("Insufficient balance")


class SearchLogError(BookstoreError):
    """MongoDB is unavailable for the search log."""
