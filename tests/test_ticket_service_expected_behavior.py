import pytest

from app.exceptions.app_exceptions import NotFoundError, ValidationError
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


def test_create_ticket_success():
    """Тест успешного создания заявки существующим пользователем."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    # Сначала создаем пользователя
    user_service = UserService(user_repo)
    user = user_service.create_user("Иван Петров", "ivan@example.com")

    ticket_service = TicketService(ticket_repo, user_repo)
    ticket = ticket_service.create_ticket(
        title="Ошибка входа",
        description="Пользователь не может войти в систему.",
        created_by_user_id=user.id,
    )

    assert ticket.id == 1
    assert ticket.title == "Ошибка входа"
    assert ticket.created_by_user_id == user.id


def test_create_ticket_with_empty_title_should_raise_error():
    """Тест создания заявки с пустым заголовком."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    user_service = UserService(user_repo)
    user = user_service.create_user("Иван Петров", "ivan@example.com")

    ticket_service = TicketService(ticket_repo, user_repo)

    with pytest.raises(ValidationError) as exc_info:
        ticket_service.create_ticket(
            title="",
            description="Описание заявки",
            created_by_user_id=user.id,
        )
    assert "Заголовок заявки не может быть пустым" in str(exc_info.value)


def test_create_ticket_for_unknown_user_should_raise_error():
    """Тест создания заявки для несуществующего пользователя."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    ticket_service = TicketService(ticket_repo, user_repo)

    with pytest.raises(NotFoundError) as exc_info:
        ticket_service.create_ticket(
            title="Ошибка входа",
            description="Пользователь не может войти в систему.",
            created_by_user_id=999,
        )
    assert "Пользователь с ID 999 не найден" in str(exc_info.value)


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


def test_list_user_tickets_should_return_only_selected_user_tickets():
    """Тест получения заявок конкретного пользователя."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    user_service = UserService(user_repo)
    user1 = user_service.create_user("Иван Петров", "ivan@example.com")
    user2 = user_service.create_user("Петр Иванов", "petr@example.com")

    ticket_service = TicketService(ticket_repo, user_repo)

    ticket_service.create_ticket("Заявка 1", "Описание 1", created_by_user_id=user1.id)
    ticket_service.create_ticket("Заявка 2", "Описание 2", created_by_user_id=user2.id)

    user_1_tickets = ticket_service.list_user_tickets(user_id=user1.id)

    assert len(user_1_tickets) == 1
    assert user_1_tickets[0].created_by_user_id == user1.id


def test_list_user_tickets_for_unknown_user_should_raise_error():
    """Тест получения заявок несуществующего пользователя."""
    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    ticket_service = TicketService(ticket_repo, user_repo)

    with pytest.raises(NotFoundError) as exc_info:
        ticket_service.list_user_tickets(user_id=999)
    assert "Пользователь с ID 999 не найден" in str(exc_info.value)