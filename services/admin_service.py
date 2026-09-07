from exceptions import InvalidInputError, BookNotFoundError
from models import Book


class AdminService:
    def __init__(self, book_repository):
        self._books = book_repository

    def list_books(self):
        return self._books.get_all()

    def get_book(self, book_id):
        book = self._books.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(book_id)
        return book

    def add_book(self, title, author, price, stock):
        self._validate(title, author, price, stock)
        self._books.add(Book(id=None, title=title.strip(), author=author.strip(), price=price, stock=stock))

    def update_book(self, book_id, title, author, price, stock):
        self._validate(title, author, price, stock)
        book = Book(id=book_id, title=title.strip(), author=author.strip(), price=price, stock=stock)
        if not self._books.update(book):
            raise BookNotFoundError(book_id)

    def delete_book(self, book_id):
        if not self._books.delete(book_id):
            raise BookNotFoundError(book_id)

    def import_from_file(self, filename):
        added = 0
        with open(filename, encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) != 4:
                    continue  # пропускаем некорректные строки
                title, author, price, stock = parts
                price = float(price)
                stock = int(stock)
                self._books.upsert_by_title_author(title.strip(), author.strip(), price, stock)
                added += stock
        self._books.commit()
        return added

    @staticmethod
    def _validate(title, author, price, stock):
        if not title or not title.strip() or not author or not author.strip():
            raise InvalidInputError("Title and author cannot be empty")
        if price < 0 or stock < 0:
            raise InvalidInputError("Price and stock cannot be negative")
