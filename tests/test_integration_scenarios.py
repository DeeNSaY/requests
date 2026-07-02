"""
Интеграционные тестовые сценарии для модулей Пользователи и Заявки.
Тестирование взаимодействия между модулями.
"""

import pytest

from app.exceptions.app_exceptions import (
    DuplicateError,
    NotFoundError,
    ValidationError
)
from app.models.ticket_status import TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


class TestIntegrationScenarios:
    """
    Класс с интеграционными тестами для проверки взаимодействия
    модулей Пользователи и Заявки.
    """

    @pytest.fixture
    def setup_services(self):
        """Фикстура для создания сервисов с общими репозиториями."""
        user_repo = UserRepository()
        ticket_repo = TicketRepository()
        user_service = UserService(user_repo)
        ticket_service = TicketService(ticket_repo, user_repo)
        return user_service, ticket_service

    @pytest.fixture
    def setup_user_and_ticket(self, setup_services):
        """Фикстура для создания пользователя и заявки."""
        user_service, ticket_service = setup_services
        user = user_service.create_user("Иван Петров", "ivan@example.com")
        ticket = ticket_service.create_ticket(
            "Тестовая заявка",
            "Описание тестовой заявки",
            user.id
        )
        return user_service, ticket_service, user, ticket

    # ============ СЦЕНАРИЙ 1: Создание заявки существующим пользователем ============

    def test_create_ticket_existing_user_success(self, setup_services):
        """
        Сценарий 1: Успешное создание заявки существующим пользователем.

        Шаги:
        1. Создать пользователя
        2. Создать заявку от имени пользователя
        3. Проверить, что заявка создана с правильными данными
        """
        user_service, ticket_service = setup_services

        # Шаг 1: Создание пользователя
        user = user_service.create_user("Иван Петров", "ivan@example.com")
        assert user.id == 1
        assert user.is_active is True

        # Шаг 2: Создание заявки
        ticket = ticket_service.create_ticket(
            title="Проблема с входом",
            description="Не могу войти в личный кабинет",
            created_by_user_id=user.id
        )

        # Шаг 3: Проверка
        assert ticket.id == 1
        assert ticket.title == "Проблема с входом"
        assert ticket.created_by_user_id == user.id
        assert ticket.status == TicketStatus.OPEN

        # Проверка через репозиторий
        saved_ticket = ticket_service.get_ticket(ticket.id)
        assert saved_ticket is not None
        assert saved_ticket.title == ticket.title

    # ============ СЦЕНАРИЙ 2: Запрет создания заявки несуществующим пользователем ============

    def test_create_ticket_nonexistent_user_error(self, setup_services):
        """
        Сценарий 2: Попытка создания заявки для несуществующего пользователя.

        Шаги:
        1. Попытаться создать заявку с несуществующим ID пользователя
        2. Проверить, что выбрасывается ошибка NotFoundError
        """
        _, ticket_service = setup_services

        # Шаг 1: Попытка создания заявки
        with pytest.raises(NotFoundError) as exc_info:
            ticket_service.create_ticket(
                title="Тестовая заявка",
                description="Описание",
                created_by_user_id=999  # Несуществующий ID
            )

        # Шаг 2: Проверка ошибки
        assert "Пользователь с ID 999 не найден" in str(exc_info.value)

    # ============ СЦЕНАРИЙ 3: Запрет создания заявки для неактивного пользователя ============

    def test_create_ticket_inactive_user_error(self, setup_services):
        """
        Сценарий 3: Попытка создания заявки для неактивного пользователя.

        Шаги:
        1. Создать пользователя
        2. Деактивировать пользователя
        3. Попытаться создать заявку
        4. Проверить, что выбрасывается ошибка ValidationError
        """
        user_service, ticket_service = setup_services

        # Шаг 1: Создание пользователя
        user = user_service.create_user("Иван Петров", "ivan@example.com")

        # Шаг 2: Деактивация пользователя
        deactivated_user = user_service.deactivate_user(user.id)
        assert deactivated_user.is_active is False

        # Шаг 3: Попытка создания заявки
        with pytest.raises(ValidationError) as exc_info:
            ticket_service.create_ticket(
                title="Тестовая заявка",
                description="Описание",
                created_by_user_id=user.id
            )

        # Шаг 4: Проверка ошибки
        assert "Нельзя создать заявку для неактивного пользователя" in str(exc_info.value)

    # ============ СЦЕНАРИЙ 4: Получение заявок конкретного пользователя ============

    def test_list_user_tickets_filtering(self, setup_services):
        """
        Сценарий 4: Получение заявок конкретного пользователя.

        Шаги:
        1. Создать двух пользователей
        2. Создать заявки для каждого пользователя
        3. Получить заявки первого пользователя
        4. Проверить, что возвращены только его заявки
        """
        user_service, ticket_service = setup_services

        # Шаг 1: Создание пользователей
        user1 = user_service.create_user("Иван Петров", "ivan@example.com")
        user2 = user_service.create_user("Петр Иванов", "petr@example.com")

        # Шаг 2: Создание заявок
        ticket1 = ticket_service.create_ticket(
            "Заявка 1", "Описание 1", user1.id
        )
        ticket2 = ticket_service.create_ticket(
            "Заявка 2", "Описание 2", user1.id
        )
        ticket3 = ticket_service.create_ticket(
            "Заявка 3", "Описание 3", user2.id
        )

        # Шаг 3: Получение заявок первого пользователя
        user1_tickets = ticket_service.list_user_tickets(user1.id)

        # Шаг 4: Проверка
        assert len(user1_tickets) == 2
        assert all(t.created_by_user_id == user1.id for t in user1_tickets)
        assert ticket1 in user1_tickets
        assert ticket2 in user1_tickets
        assert ticket3 not in user1_tickets

    # ============ СЦЕНАРИЙ 5: Изменение статуса заявки ============

    def test_change_ticket_status_workflow(self, setup_user_and_ticket):
        """
        Сценарий 5: Полный цикл изменения статуса заявки.

        Шаги:
        1. Создать заявку (статус OPEN)
        2. Изменить статус на IN_PROGRESS
        3. Проверить изменение статуса
        4. Изменить статус на CLOSED
        5. Проверить изменение статуса
        6. Попытаться изменить статус несуществующей заявки
        """
        user_service, ticket_service, user, ticket = setup_user_and_ticket

        # Шаг 1: Проверка начального статуса
        assert ticket.status == TicketStatus.OPEN

        # Шаг 2: Изменение статуса на IN_PROGRESS
        updated_ticket = ticket_service.change_status(
            ticket.id,
            TicketStatus.IN_PROGRESS
        )

        # Шаг 3: Проверка
        assert updated_ticket.status == TicketStatus.IN_PROGRESS
        # Проверка через репозиторий
        retrieved_ticket = ticket_service.get_ticket(ticket.id)
        assert retrieved_ticket.status == TicketStatus.IN_PROGRESS

        # Шаг 4: Изменение статуса на CLOSED
        updated_ticket = ticket_service.change_status(
            ticket.id,
            TicketStatus.CLOSED
        )

        # Шаг 5: Проверка
        assert updated_ticket.status == TicketStatus.CLOSED
        retrieved_ticket = ticket_service.get_ticket(ticket.id)
        assert retrieved_ticket.status == TicketStatus.CLOSED

        # Шаг 6: Попытка изменения статуса несуществующей заявки
        with pytest.raises(NotFoundError) as exc_info:
            ticket_service.change_status(999, TicketStatus.CLOSED)
        assert "Заявка с ID 999 не найдена" in str(exc_info.value)

