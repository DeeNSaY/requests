from app.models.user import User


class UserRepository:
    """Репозиторий пользователей.

    Отвечает только за хранение и получение данных.
    Бизнес-логика и проверки находятся в сервисах.
    """

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    def add(self, full_name: str, email: str) -> User:
        user = User(
            id=self._next_id,
            full_name=full_name,
            email=email,
        )
        self._users[user.id] = user
        self._next_id += 1
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def get_all(self) -> list[User]:
        return list(self._users.values())

    def find_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def deactivate(self, user_id: int) -> User | None:
        user = self.get_by_id(user_id)
        if user is not None:
            user.is_active = False
        return user
