def is_valid_email(email: str) -> bool:
    """Простая проверка email для учебного проекта."""
    if not email:
        return False

    if "@" not in email:
        return False

    # Разделяем email на локальную часть и домен
    parts = email.split("@")
    if len(parts) != 2:
        return False

    local_part = parts[0]
    domain = parts[1]

    # Проверяем, что локальная часть не пустая
    if not local_part:
        return False

    # Проверяем, что домен содержит точку и не пустой
    if not domain or "." not in domain:
        return False

    # Проверяем, что домен не начинается и не заканчивается точкой
    if domain.startswith(".") or domain.endswith("."):
        return False

    return True


def is_not_empty(value: str) -> bool:
    """Проверяет, что строка не пустая."""
    return bool(value and value.strip())