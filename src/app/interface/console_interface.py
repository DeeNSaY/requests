from app.exceptions.app_exceptions import AppError
from app.models.ticket_status import TicketStatus
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


class ConsoleInterface:
    """Консольный интерфейс приложения.

    Интерфейс отвечает только за ввод и вывод данных.
    Бизнес-логика находится в сервисах.
    """

    def __init__(self, user_service: UserService, ticket_service: TicketService) -> None:
        self._user_service = user_service
        self._ticket_service = ticket_service

    def run_demo(self) -> None:
        print("Демонстрация работы системы учета заявок")
        print("-" * 45)

        try:
            user = self._user_service.create_user(
                full_name="Иван Петров",
                email="ivan.petrov@example.com",
            )
            print(f"Создан пользователь: {user.id} | {user.full_name} | {user.email}")

            ticket = self._ticket_service.create_ticket(
                title="Не открывается личный кабинет",
                description="Пользователь не может войти в систему после смены пароля.",
                created_by_user_id=user.id,
            )
            print(f"Создана заявка: {ticket.id} | {ticket.title} | статус: {ticket.status.value}")

            self._ticket_service.change_status(ticket.id, TicketStatus.IN_PROGRESS)
            updated_ticket = self._ticket_service.get_ticket(ticket.id)
            print(f"Статус заявки изменен: {updated_ticket.status.value}")

            print("\nСписок заявок пользователя:")
            for item in self._ticket_service.list_user_tickets(user.id):
                print(f"- #{item.id}: {item.title}")

        except AppError as error:
            print(f"Ошибка приложения: {error}")
