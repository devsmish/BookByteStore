import os
import pymysql
from dotenv import load_dotenv
from app.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

db_name = os.getenv("MYSQL_DB_NAME")

config_read = {
    "host": os.getenv("MYSQL_READ_HOST"),
    "port": int(os.getenv("MYSQL_READ_PORT", 3306)),
    "user": os.getenv("MYSQL_READ_USER"),
    "password": os.getenv("MYSQL_READ_PASSWORD"),
}

config_edit = {
    "host": os.getenv("MYSQL_EDIT_HOST"),
    "port": int(os.getenv("MYSQL_EDIT_PORT", 3306)),
    "user": os.getenv("MYSQL_EDIT_USER"),
    "password": os.getenv("MYSQL_EDIT_PASSWORD"),
}


class DatabaseConnectionError(Exception):
    """A clear error message instead of a raw traceback from PyMySQL."""


def _connect(config, role, database=None):
    missing = [k for k in ("host", "user", "password") if not config.get(k)]
    if missing:
        env_vars = ", ".join(f"MYSQL_{role.upper()}_{m.upper()}" for m in missing)
        logger.error("Missing env vars for %s connection: %s", role, env_vars)
        raise DatabaseConnectionError(
            f"Environment variables for the {role} connection are not set: " f"{env_vars}. Check the .env file!!!"
        )

    conn_kwargs = config.copy()
    if database:
        conn_kwargs["database"] = database

    try:
        return pymysql.connect(**conn_kwargs)
    except pymysql.err.OperationalError as e:
        logger.error("Failed to connect to MySQL (%s, host=%s): %s", role, config["host"], e)
        raise DatabaseConnectionError(f"Failed to connect to MySQL ({role}, host={config['host']}): {e}") from e


def get_read_connection(select_db: bool = True):
    return _connect(config_read, "read", database=db_name if select_db else None)


def get_edit_connection(select_db: bool = True):
    return _connect(config_edit, "edit", database=db_name if select_db else None)


def init_db():
    """Creates the database and tables. Requires an edit user with the CREATE privilege."""
    with get_edit_connection(select_db=False) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200),
                    author VARCHAR(100),
                    price DECIMAL(10,2),
                    stock INT CHECK (stock >= 0),
                    deleted_at DATETIME NULL DEFAULT NULL
                )
            """)

            try:
                cursor.execute("""
                    ALTER TABLE books
                    ADD COLUMN deleted_at DATETIME NULL DEFAULT NULL
                """)
            except pymysql.err.OperationalError as e:
                if e.args[0] != 1060:  # 1060: Duplicate column name
                    raise

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE,
                    password VARCHAR(255),
                    balance DECIMAL(10,2) CHECK (balance >= 0),
                    is_admin BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    book_id INT,
                    quantity INT,
                    purchase_date DATE,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (book_id) REFERENCES books(id)
                )
            """)
            connection.commit()
