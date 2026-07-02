# app/repositories/ticket_repository.py
from app.models.ticket import Ticket
from app.models.ticket_status import TicketStatus


class TicketRepository:
    """Репозиторий заявок."""

    def __init__(self) -> None:
        self._tickets: dict[int, Ticket] = {}
        self._next_id = 1

    def add(self, title: str, description: str, created_by_user_id: int) -> Ticket:
        ticket = Ticket(
            id=self._next_id,
            title=title,
            description=description,
            created_by_user_id=created_by_user_id,
        )
        self._tickets[ticket.id] = ticket
        self._next_id += 1
        return ticket

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def get_all(self) -> list[Ticket]:
        return list(self._tickets.values())

    def list_by_user_id(self, user_id: int) -> list[Ticket]:
        # Исправлено: фильтруем заявки по пользователю
        return [ticket for ticket in self._tickets.values() 
                if ticket.created_by_user_id == user_id]

    def update_status(self, ticket_id: int, status: TicketStatus) -> Ticket | None:
        ticket = self.get_by_id(ticket_id)
        if ticket is not None:
            # Исправлено: устанавливаем переданный статус
            ticket.status = status
        return ticket