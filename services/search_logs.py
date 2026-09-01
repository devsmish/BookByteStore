import os
from pymongo import MongoClient
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

collection = client[os.getenv("MONGO_DB_NAME", "ich_edit")][
    os.getenv("MONGO_COLLECTION_NAME", "bookstore_logs_searches")
]


def log_search(query):
    if query.strip():
        collection.insert_one({"query": query.strip().lower()})


def show_popular_queries():
    queries = [doc["query"] for doc in collection.find() if doc.get("query")]

    counter = Counter(queries)
    top = counter.most_common(5)

    if not top:
        print("No search data found.")
        return

    print("Most frequent search queries:")
    for i, (q, count) in enumerate(top, 1):
        print(f"{i}. {q} — {count} times")
