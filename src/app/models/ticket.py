from dataclasses import dataclass

from app.models.ticket_status import TicketStatus


@dataclass
class Ticket:
    id: int
    title: str
    description: str
    created_by_user_id: int
    status: TicketStatus = TicketStatus.OPEN
