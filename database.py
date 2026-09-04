import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

db_name = os.getenv("MYSQL_DB_NAME")

# read — SELECT only (viewing books, login)
config_read = {
    'host': os.getenv("MYSQL_READ_HOST"),
    'port': int(os.getenv("MYSQL_READ_PORT", 3306)),
    'user': os.getenv("MYSQL_READ_USER"),
    'password': os.getenv("MYSQL_READ_PASSWORD"),
}

# edit — INSERT/UPDATE (registration, purchase, book downloading, database creation)
config_edit = {
    'host': os.getenv("MYSQL_EDIT_HOST"),
    'port': int(os.getenv("MYSQL_EDIT_PORT", 3306)),
    'user': os.getenv("MYSQL_EDIT_USER"),
    'password': os.getenv("MYSQL_EDIT_PASSWORD"),
}


class DatabaseConnectionError(Exception):
    """A clear error message instead of a raw traceback from PyMySQL."""


def _connect(config, role):
    missing = [k for k in ("host", "user", "password") if not config.get(k)]
    if missing:
        raise DatabaseConnectionError(
            f"Environment variables for the {role} connection are not set: "
            f"{', '.join(f'MYSQL_{role.upper()}_{m.upper()}' for m in missing)}. "
            f"Check the .env file!!!"
        )
    try:
        return pymysql.connect(**config)
    except pymysql.err.OperationalError as e:
        raise DatabaseConnectionError(
            f"Failed to connect to MySQL ({role}, host={config['host']}): {e}"
        ) from e

def get_read_connection():
    return _connect(config_read, "read")


def get_edit_connection():
    return _connect(config_edit, "edit")


def init_db():
    """Creates the database and tables. Requires an edit user with the CREATE privilege."""
    with get_edit_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200),
                    author VARCHAR(100),
                    price DECIMAL(10,2),
                    stock INT CHECK (stock >= 0)
                )
            """)


            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE,
                    password VARCHAR(255),
                    balance DECIMAL(10,2) CHECK (balance >= 0)
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
