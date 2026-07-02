# app/services/user_service.py
from app.exceptions.app_exceptions import DuplicateError, NotFoundError, ValidationError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.validators import is_valid_email


class UserService:
    """Сервис пользователей."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def create_user(self, full_name: str, email: str) -> User:
        full_name = full_name.strip()
        email = email.strip().lower()

        if not full_name:
            raise ValidationError("ФИО пользователя не может быть пустым.")

        if not is_valid_email(email):
            raise ValidationError("Некорректный email пользователя.")

        if self._user_repository.find_by_email(email) is not None:
            raise DuplicateError("Пользователь с таким email уже существует.")

        return self._user_repository.add(full_name=full_name, email=email)

    def get_user(self, user_id: int) -> User:
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден.")
        return user

    def list_users(self) -> list[User]:
        return self._user_repository.get_all()

    def list_active_users(self) -> list[User]:
        # Исправлено: фильтруем только активных пользователей
        return [user for user in self._user_repository.get_all() if user.is_active]

    def deactivate_user(self, user_id: int) -> User:
        user = self._user_repository.deactivate(user_id)
        if user is None:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден.")
        return user