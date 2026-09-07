from config import is_admin
from exceptions import InvalidInputError, UsernameTakenError, InvalidCredentialsError
from models import User


class AuthService:
    def __init__(self, user_repository):
        self._users = user_repository

    def register(self, username, password, balance):
        username = username.strip()
        password = password.strip()

        if not username or not password:
            raise InvalidInputError("Username and password cannot be empty")
        if balance < 0:
            raise InvalidInputError("Balance cannot be negative")
        if self._users.username_exists(username):
            raise UsernameTakenError(username)

        user_id = self._users.create(username, password, balance)
        return User(id=user_id, username=username, balance=balance, is_admin=is_admin(username))

    def login(self, username, password):
        user = self._users.authenticate(username.strip(), password.strip())
        if not user:
            raise InvalidCredentialsError()
        user.is_admin = is_admin(user.username)
        return user
