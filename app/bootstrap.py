"""Assembling repositories and services from pre-configured read/edit connections.

A shared entry point for `main.py` (CLI) and `gui_main.py` (GUI) to prevent both entry
points from duplicating the list of repositories/services or drifting out of sync over time.
"""
from dataclasses import dataclass

from app.db.books import BookRepository
from app.db.purchases import PurchaseRepository
from app.db.users import UserRepository
from app.services.admin_service import AdminService
from app.services.auth import AuthService
from app.services.catalog_service import CatalogService
from app.services.purchase_service import PurchaseService
from app.services.search_logs import SearchLogRepository


@dataclass
class Services:
    auth: AuthService
    catalog: CatalogService
    purchase: PurchaseService
    admin: AdminService


def build_services(read_connection, edit_connection):
    book_repository = BookRepository(read_connection, edit_connection)
    user_repository = UserRepository(read_connection, edit_connection)
    purchase_repository = PurchaseRepository(read_connection, edit_connection)
    search_log_repository = SearchLogRepository()

    auth_service = AuthService(user_repository)
    catalog_service = CatalogService(book_repository, search_log_repository)
    purchase_service = PurchaseService(book_repository, user_repository, purchase_repository, edit_connection)
    admin_service = AdminService(book_repository)

    return Services(
        auth=auth_service,
        catalog=catalog_service,
        purchase=purchase_service,
        admin=admin_service,
    )
