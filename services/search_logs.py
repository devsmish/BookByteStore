import os
from collections import Counter

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

from exceptions import SearchLogError

load_dotenv()


class SearchLogRepository:
    def __init__(self):
        client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=3000)
        self._collection = client[os.getenv("MONGO_DB_NAME", "ich_edit")][
            os.getenv("MONGO_COLLECTION_NAME", "bookstore_logs_searches")
        ]

    def log(self, query):
        query = query.strip().lower()
        if not query:
            return
        try:
            self._collection.insert_one({"query": query})
        except PyMongoError as e:
            raise SearchLogError(str(e)) from e

    def popular(self, limit=5):
        try:
            queries = [doc["query"] for doc in self._collection.find() if doc.get("query")]
        except PyMongoError as e:
            raise SearchLogError(str(e)) from e

        return Counter(queries).most_common(limit)
