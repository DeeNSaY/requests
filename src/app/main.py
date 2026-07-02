from app.interface.console_interface import ConsoleInterface
from app.services.application_service import ApplicationService


def main() -> None:
    application = ApplicationService()

    console = ConsoleInterface(
        user_service=application.user_service,
        ticket_service=application.ticket_service,
    )
    console.run_demo()


if __name__ == "__main__":
    main()