import pytest

from app.exceptions.app_exceptions import NotFoundError, ValidationError
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


def test_create_ticket_success():
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    user = user_service.create_user("Test User", "test@example.com")

    ticket_service = TicketService(TicketRepository(), user_repository)

    ticket = ticket_service.create_ticket(
        title="Ошибка входа",
        description="Пользователь не может войти в систему.",
        created_by_user_id=user.id,
    )


def test_create_ticket_with_empty_title_should_raise_error():
    ticket_service = TicketService(TicketRepository(), UserRepository())

    with pytest.raises(ValidationError):
        ticket_service.create_ticket(
            title="",
            description="Описание заявки",
            created_by_user_id=1,
        )


def test_create_ticket_for_unknown_user_should_raise_error():
    user_service = UserService(UserRepository())
    ticket_service = TicketService(TicketRepository(), UserRepository())

    with pytest.raises(NotFoundError):
        ticket_service.create_ticket(
            title="Ошибка входа",
            description="Пользователь не может войти в систему.",
            created_by_user_id=999,
        )


def test_list_user_tickets_should_return_only_selected_user_tickets():
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    user1 = user_service.create_user("User 1", "user1@example.com")
    user2 = user_service.create_user("User 2", "user2@example.com")

    ticket_repository = TicketRepository()
    ticket_service = TicketService(ticket_repository, user_repository)

    ticket_service.create_ticket("Заявка 1", "Описание 1", created_by_user_id=user1.id)
    ticket_service.create_ticket("Заявка 2", "Описание 2", created_by_user_id=user2.id)

    user_1_tickets = ticket_service.list_user_tickets(user_id=user1.id)
