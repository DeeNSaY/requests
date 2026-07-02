import pytest

from app.exceptions.app_exceptions import ValidationError, NotFoundError
from app.models.ticket_status import TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


def test_create_user_with_empty_email_local_part_should_raise_error():
    """Тест создания пользователя с email без локальной части."""
    service = UserService(UserRepository())

    with pytest.raises(ValidationError) as exc_info:
        service.create_user("Test User", "@example.com")
    assert "Некорректный email" in str(exc_info.value)


def test_create_user_with_email_without_domain_should_raise_error():
    """Тест создания пользователя с email без домена."""
    service = UserService(UserRepository())

    with pytest.raises(ValidationError) as exc_info:
        service.create_user("Test User", "user@")
    assert "Некорректный email" in str(exc_info.value)


def test_create_user_with_email_without_at_symbol_should_raise_error():
    """Тест создания пользователя с email без @."""
    service = UserService(UserRepository())

    with pytest.raises(ValidationError) as exc_info:
        service.create_user("Test User", "invalid-email")
    assert "Некорректный email" in str(exc_info.value)


def test_create_user_with_email_with_domain_starting_with_dot_should_raise_error():
    """Тест создания пользователя с email, где домен начинается с точки."""
    service = UserService(UserRepository())

    with pytest.raises(ValidationError) as exc_info:
        service.create_user("Test User", "user@.example.com")
    assert "Некорректный email" in str(exc_info.value)


def test_list_active_users_should_not_return_deactivated_users():
    """Тест получения списка активных пользователей."""
    service = UserService(UserRepository())

    active_user = service.create_user("Active User", "active@example.com")
    inactive_user = service.create_user("Inactive User", "inactive@example.com")
    service.deactivate_user(inactive_user.id)

    active_users = service.list_active_users()

    assert active_users == [active_user]
    assert len(active_users) == 1
    assert all(user.is_active for user in active_users)


def test_change_status_should_store_requested_status():
    """Тест изменения статуса заявки."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    user_service = UserService(user_repo)
    user = user_service.create_user("Иван Петров", "ivan@example.com")

    ticket_service = TicketService(ticket_repo, user_repo)
    ticket = ticket_service.create_ticket(
        title="Status check",
        description="The ticket status should be changed.",
        created_by_user_id=user.id,
    )

    updated_ticket = ticket_service.change_status(ticket.id, TicketStatus.CLOSED)

    assert updated_ticket.status == TicketStatus.CLOSED

    # Проверяем, что статус сохранился в репозитории
    retrieved_ticket = ticket_service.get_ticket(ticket.id)
    assert retrieved_ticket.status == TicketStatus.CLOSED


def test_create_ticket_with_empty_description_should_raise_error():
    """Тест создания заявки с пустым описанием."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    user_service = UserService(user_repo)
    user = user_service.create_user("Иван Петров", "ivan@example.com")

    ticket_service = TicketService(ticket_repo, user_repo)

    with pytest.raises(ValidationError) as exc_info:
        ticket_service.create_ticket(
            title="Заголовок",
            description="",
            created_by_user_id=user.id,
        )
    assert "Описание заявки не может быть пустым" in str(exc_info.value)


def test_create_ticket_with_whitespace_only_should_raise_error():
    """Тест создания заявки с пробелами в заголовке и описании."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    user_service = UserService(user_repo)
    user = user_service.create_user("Иван Петров", "ivan@example.com")

    ticket_service = TicketService(ticket_repo, user_repo)

    with pytest.raises(ValidationError) as exc_info:
        ticket_service.create_ticket(
            title="   ",
            description="Описание",
            created_by_user_id=user.id,
        )
    assert "Заголовок заявки не может быть пустым" in str(exc_info.value)


def test_create_ticket_for_inactive_user_should_raise_error():
    """Тест создания заявки для неактивного пользователя."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    user_service = UserService(user_repo)
    user = user_service.create_user("Иван Петров", "ivan@example.com")
    user_service.deactivate_user(user.id)

    ticket_service = TicketService(ticket_repo, user_repo)

    with pytest.raises(ValidationError) as exc_info:
        ticket_service.create_ticket(
            title="Ошибка входа",
            description="Пользователь не может войти в систему.",
            created_by_user_id=user.id,
        )
    assert "Нельзя создать заявку для неактивного пользователя" in str(exc_info.value)


def test_list_user_tickets_for_unknown_user_should_raise_error():
    """Тест получения заявок несуществующего пользователя."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    ticket_service = TicketService(ticket_repo, user_repo)

    with pytest.raises(NotFoundError) as exc_info:
        ticket_service.list_user_tickets(user_id=999)
    assert "Пользователь с ID 999 не найден" in str(exc_info.value)