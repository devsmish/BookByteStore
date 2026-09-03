from dotenv import load_dotenv
import os
import pymysql

load_dotenv()


# read
config_read = {'host': os.getenv("MYSQL_READ_HOST"),
               'port': int(os.getenv("MYSQL_READ_PORT", 3306)),
               'user': os.getenv("MYSQL_READ_USER"),
               'password': os.getenv("MYSQL_READ_PASSWORD"),
               'database': os.getenv("MYSQL_READ_DB"),
               }

# edit
config_edit = {'host': os.getenv("MYSQL_EDIT_HOST"),
               'port': int(os.getenv("MYSQL_EDIT_PORT", 3306)),
               'user': os.getenv("MYSQL_EDIT_USER"),
               'password': os.getenv("MYSQL_EDIT_PASSWORD"),
               'database': os.getenv("MYSQL_EDIT_DB"),
               }

with pymysql.connect(**config_edit) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM country")
        for country in cursor.fetchmany(5):
            print(country)
