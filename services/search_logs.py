import os

from pymongo import MongoClient
from collections import Counter

client = MongoClient(os.getenv("MONGO_URI"))

collection = client[os.getenv("MONGO_DATABASE")][os.getenv("MONGO_COLLECTION")]


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
