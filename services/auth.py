from db import users


def register(edit_connection):
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    if not username or not password:
        print("Username and password cannot be empty")
        return

    try:
        balance = float(input("Enter balance: "))
        if balance < 0:
            raise ValueError
    except ValueError:
        print("Invalid balance")
        return

    if users.create_user(edit_connection, username, password, balance):
        print("Registration successful")
    else:
        print("Username already exists")


def login(read_connection):
    username = input("Enter username: ")
    password = input("Enter password: ")

    user = users.get_user(read_connection, username, password)

    if not user:
        print("Invalid username or password")
        return None

    print("Login successful")
    return user[0], user[1]
