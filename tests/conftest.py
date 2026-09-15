from datetime import datetime
from decimal import Decimal

import pytest

from app.models import Book, Purchase


class FakeBookRepo:
    """It replicates the SQL conditions of the actual BookRepository (deleted_at IS NULL,
    stock >= quantity) rather than simply storing books in a dictionary without constraints."""

    def __init__(self, books=None):
        self.books = books or {
            1: Book(id=1, title="Dune", author="Herbert", price=Decimal("10.00"), stock=5, deleted_at=None)
        }
        self.next_id = max(self.books, default=0) + 1

    def get_all(self):
        return [b for b in self.books.values() if b.stock > 0 and b.deleted_at is None]

    def search(self, query, only_in_stock=True):
        q = query.lower()
        results = [
            b for b in self.books.values()
            if b.deleted_at is None and (q in b.title.lower() or q in b.author.lower())
        ]
        if only_in_stock:
            results = [b for b in results if b.stock > 0]
        return results

    def get_by_id(self, book_id, include_deleted=False):
        b = self.books.get(book_id)
        if not b:
            return None
        if not include_deleted and b.deleted_at is not None:
            return None
        return b

    def get_deleted(self):
        return [b for b in self.books.values() if b.deleted_at is not None]

    def decrease_stock(self, book_id, qty):
        b = self.books.get(book_id)
        if not b or b.deleted_at is not None or b.stock < qty:
            return 0
        b.stock -= qty
        return 1

    def add(self, book):
        book.id = self.next_id
        self.next_id += 1
        self.books[book.id] = book

    def update(self, book):
        existing = self.books.get(book.id)
        if not existing or existing.deleted_at is not None:
            return 0
        self.books[book.id] = book
        return 1

    def delete(self, book_id):
        b = self.books.get(book_id)
        if not b or b.deleted_at is not None:
            return 0
        b.deleted_at = datetime.now()
        return 1

    def restore(self, book_id):
        b = self.books.get(book_id)
        if not b or b.deleted_at is None:
            return 0
        b.deleted_at = None
        return 1

    def upsert_by_title_author(self, title, author, price, added_stock):
        for b in self.books.values():
            if b.title == title and b.author == author and b.deleted_at is None:
                b.stock += added_stock
                return
        self.add(Book(id=None, title=title, author=author, price=price, stock=added_stock))

    def commit(self):
        pass


class FakeUserRepo:
    def __init__(self, users=None):
        self.users = users or {}
        self.passwords = {}
        self.next_id = max(self.users, default=0) + 1

    def username_exists(self, username):
        return any(u.username == username for u in self.users.values())

    def create(self, username, password, balance):
        uid = self.next_id
        self.next_id += 1
        from app.models import User
        self.users[uid] = User(id=uid, username=username, balance=balance)
        self.passwords[uid] = password
        return uid

    def authenticate(self, username, password):
        for uid, u in self.users.items():
            if u.username == username and self.passwords.get(uid) == password:
                return u
        return None

    def decrease_balance(self, user_id, amount):
        u = self.users[user_id]
        if u.balance < amount:
            return 0
        u.balance -= amount
        return 1

    def increase_balance(self, user_id, amount):
        self.users[user_id].balance += amount
        return 1

    def get_balance(self, user_id):
        return self.users[user_id].balance


class FakePurchaseRepo:
    """A snapshot of title/author/price at the time of purchase is like a real JOIN,
    only materialized immediately rather than upon every read."""

    def __init__(self, book_repo=None):
        self.log = []
        self._book_repo = book_repo

    def add(self, user_id, book_id, quantity):
        book = self._book_repo.get_by_id(book_id, include_deleted=True) if self._book_repo else None
        self.log.append(Purchase(
            purchase_date="2026-08-19",
            title=book.title if book else "?",
            author=book.author if book else "?",
            quantity=quantity,
            price=book.price if book else Decimal("0"),
            total=(book.price * quantity) if book else Decimal("0"),
        ))

    def get_by_user(self, user_id):
        return self.log


class FakeConnection:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


@pytest.fixture
def book_repo():
    return FakeBookRepo()


@pytest.fixture
def user_repo():
    return FakeUserRepo()


@pytest.fixture
def purchase_repo(book_repo):
    return FakePurchaseRepo(book_repo)


@pytest.fixture
def connection():
    return FakeConnection()


class FakeSearchLogRepo:
    def __init__(self, fail=False):
        self.logged = []
        self.fail = fail

    def log(self, query):
        if self.fail:
            from app.exceptions import SearchLogError
            raise SearchLogError("mongo down")
        self.logged.append(query.strip().lower())

    def popular(self, limit=5):
        if self.fail:
            from app.exceptions import SearchLogError
            raise SearchLogError("mongo down")
        from collections import Counter
        return Counter(self.logged).most_common(limit)


@pytest.fixture
def search_log_repo():
    return FakeSearchLogRepo()
