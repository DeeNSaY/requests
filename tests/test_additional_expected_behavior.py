import pytest

from app.exceptions.app_exceptions import ValidationError
from app.models.ticket_status import TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


def test_create_user_with_empty_email_local_part_should_raise_error():
    service = UserService(UserRepository())

    with pytest.raises(ValidationError):
        service.create_user("Test User", "@example.com")


def test_list_active_users_should_not_return_deactivated_users():
    service = UserService(UserRepository())

    active_user = service.create_user("Active User", "active@example.com")
    inactive_user = service.create_user("Inactive User", "inactive@example.com")
    service.deactivate_user(inactive_user.id)

    active_users = service.list_active_users()

    assert active_users == [active_user]


def test_change_status_should_store_requested_status():
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    user = user_service.create_user("Test User", "test@example.com")
    ticket_service = TicketService(TicketRepository(), user_repository)
    ticket = ticket_service.create_ticket(
        title="Status check",
        description="The ticket status should be changed.",
        created_by_user_id=1,
    )

    updated_ticket = ticket_service.change_status(ticket.id, TicketStatus.CLOSED)

    assert updated_ticket.status == TicketStatus.CLOSED
