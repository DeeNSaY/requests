import pytest

from app.exceptions.app_exceptions import DuplicateError, ValidationError
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def test_create_user_success():
    service = UserService(UserRepository())

    user = service.create_user("Иван Петров", "ivan@example.com")

    assert user.id == 1
    assert user.full_name == "Иван Петров"
    assert user.email == "ivan@example.com"
    assert user.is_active is True


def test_create_user_with_invalid_email_should_raise_error():
    service = UserService(UserRepository())

    with pytest.raises(ValidationError):
        service.create_user("Иван Петров", "invalid-email")


def test_create_duplicate_user_should_raise_error():
    service = UserService(UserRepository())

    service.create_user("Иван Петров", "ivan@example.com")

    with pytest.raises(DuplicateError):
        service.create_user("Иван Петров 2", "ivan@example.com")
