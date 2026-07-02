# app/services/application_service.py
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


class ApplicationService:
    """Собирает сервисы приложения в одном месте."""

    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.ticket_repository = TicketRepository()

        self.user_service = UserService(self.user_repository)
        self.ticket_service = TicketService(self.ticket_repository, self.user_repository)