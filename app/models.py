from dataclasses import dataclass


@dataclass
class Book:
    id: int | None
    title: str
    author: str
    price: float
    stock: int


@dataclass
class User:
    id: int
    username: str
    balance: float
    is_admin: bool = False


@dataclass
class Purchase:
    purchase_date: object
    title: str
    author: str
    quantity: int
    price: float
    total: float
