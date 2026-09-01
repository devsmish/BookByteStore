from db import users

def register(connection):
    username = input("Enter username: ")
    password = input("Enter password: ")

    try:
        balance = float(input("Enter balance: "))
        if balance < 0:
            raise ValueError
    except ValueError:
        print("Invalid balance")
        return

    if users.create_user(connection, username, password, balance):
        print("Registration successful")
    else:
        print("Username already exists")


def login(connection):
    username = input("Enter username: ")
    password = input("Enter password: ")

    user = users.get_user(connection, username, password)

    if not user:
        print("Invalid username or password")
        return None

    print("Login successful")
    return user[0]
