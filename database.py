from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

config = {'host': os.getenv("MYSQL_EDIT_HOST"),
          'port': int(os.getenv("MYSQL_EDIT_PORT", 3306)),
          'user': os.getenv("MYSQL_EDIT_USER"),
          'password': os.getenv("MYSQL_EDIT_PASSWORD"),
          'database': os.getenv("MYSQL_EDIT_DB"),
          }

db_name = config.get("database")


def get_connection():
    return pymysql.connect(**config)


def init_db():
    with get_connection() as connection:
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
                    password VARCHAR(100),
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
