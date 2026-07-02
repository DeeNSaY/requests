class AppError(Exception):
    """Базовое исключение приложения."""


class ValidationError(AppError):
    """Ошибка проверки входных данных."""


class NotFoundError(AppError):
    """Ошибка поиска объекта."""


class DuplicateError(AppError):
    """Ошибка дублирования данных."""
