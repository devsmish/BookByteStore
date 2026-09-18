from app.config import is_admin
from app.exceptions import InvalidCredentialsError, InvalidInputError, UsernameTakenError
from app.logging_config import get_logger
from app.models import User

logger = get_logger(__name__)

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
            logger.info("Registration failed: username '%s' already taken", username)
            raise UsernameTakenError(username)

        user_id = self._users.create(username, password, balance)
        logger.info("New user registered: '%s' (id=%s)", username, user_id)
        return User(id=user_id, username=username, balance=balance, is_admin=is_admin(username))

    def login(self, username, password):
        username = username.strip()
        user = self._users.authenticate(username, password.strip())
        if not user:
            logger.warning("Failed login attempt for username '%s'", username)
            raise InvalidCredentialsError()
        user.is_admin = is_admin(user.username)
        logger.info("User '%s' logged in%s", user.username, " as admin" if user.is_admin else "")
        return user
