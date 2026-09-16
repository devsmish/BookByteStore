import pytest

from app.exceptions import InvalidInputError, SearchLogError
from app.services.catalog_service import CatalogService
from tests.conftest import FakeSearchLogRepo


@pytest.fixture
def catalog_service(book_repo, search_log_repo):
    return CatalogService(book_repo, search_log_repo)


def test_list_books(catalog_service):
    books = catalog_service.list_books()
    assert len(books) == 1


def test_search_returns_matches_and_logs(catalog_service, search_log_repo):
    results, warning = catalog_service.search("dune")
    assert warning is None
    assert len(results) == 1
    assert search_log_repo.logged == ["dune"]


def test_search_empty_query_raises(catalog_service):
    with pytest.raises(InvalidInputError):
        catalog_service.search("   ")


def test_search_continues_when_logging_unavailable(book_repo):
    """If Mongo is down, the search should still work—just with a warning."""
    broken_logs = FakeSearchLogRepo(fail=True)
    service = CatalogService(book_repo, broken_logs)

    results, warning = service.search("dune")

    assert len(results) == 1
    assert warning is not None


def test_popular_queries_delegates_to_repo(catalog_service, search_log_repo):
    catalog_service.search("dune")
    catalog_service.search("dune")
    catalog_service.search("herbert")

    top = catalog_service.popular_queries()

    assert top[0] == ("dune", 2)


def test_popular_queries_propagates_error(book_repo):
    broken_logs = FakeSearchLogRepo(fail=True)
    service = CatalogService(book_repo, broken_logs)

    with pytest.raises(SearchLogError):
        service.popular_queries()
