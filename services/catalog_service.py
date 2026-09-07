from exceptions import InvalidInputError, SearchLogError


class CatalogService:
    def __init__(self, book_repository, search_log_repository):
        self._books = book_repository
        self._logs = search_log_repository

    def list_books(self):
        return self._books.get_all()

    def search(self, query):
        if not query or not query.strip():
            raise InvalidInputError("Search query cannot be empty")

        log_warning = None
        try:
            self._logs.log(query)
        except SearchLogError as e:
            log_warning = str(e)  # Search must not fail due to Mongo unavailability

        results = self._books.search(query)
        return results, log_warning

    def popular_queries(self, limit=5):
        return self._logs.popular(limit)
