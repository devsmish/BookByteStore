import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=3000)

collection = client[os.getenv("MONGO_DB_NAME", "ich_edit")][
    os.getenv("MONGO_COLLECTION_NAME", "bookstore_logs_searches")
]


def log_search(query):
    if not query.strip():
        return
    try:
        collection.insert_one({"query": query.strip().lower()})
    except PyMongoError as e:
        print(f"Search logging unavailable: {e}")


def show_popular_queries():
    try:
        queries = [doc["query"] for doc in collection.find() if doc.get("query")]
    except PyMongoError as e:
        print(f"Popular searches unavailable: {e}")
        return

    counter = Counter(queries)
    top = counter.most_common(5)

    if not top:
        print("No search data found.")
        return

    print("Most frequent search queries:")
    for i, (q, count) in enumerate(top, 1):
        print(f"{i}. {q} — {count} times")
