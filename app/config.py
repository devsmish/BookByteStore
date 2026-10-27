import os

from dotenv import load_dotenv

from app.env import get_env_path

load_dotenv(get_env_path())

_raw = os.getenv("ADMIN_USERNAMES", "")
ADMIN_USERNAMES = {name.strip() for name in _raw.split(",") if name.strip()}


def is_admin(username):
    return username in ADMIN_USERNAMES
