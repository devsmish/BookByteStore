from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Book:
    id: int | None
    title: str
    author: str
    price: Decimal
    stock: int


@dataclass
class User:
    id: int
    username: str
    balance: Decimal
    is_admin: bool = False


@dataclass
class Purchase:
    purchase_date: object
    title: str
    author: str
    quantity: int
    price: Decimal
    total: Decimal
