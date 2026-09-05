import os
from dotenv import load_dotenv

load_dotenv()

_raw = os.getenv("ADMIN_USERNAMES", "")
ADMIN_USERNAMES = {name.strip() for name in _raw.split(",") if name.strip()}


def is_admin(username):
    return username in ADMIN_USERNAMES
