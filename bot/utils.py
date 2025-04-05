# bot/utils.py

import re

def validate_phone(phone: str) -> bool:
    """
    Проверяет, что номер телефона соответствует формату 7XXXXXXXXXX.
    :param phone: Номер телефона
    :return: True, если номер корректный, иначе False
    """
    return re.match(r"^7\d{10}$", phone) is not None

def format_customer_info(customer_data: dict) -> str:
    """
    Форматирует информацию о клиенте для вывода в сообщении бота.
    :param customer_data: Данные клиента
    :return: Отформатированная строка
    """
    return (
        f"Имя: {customer_data.get('name', 'Не указано')}\n"
        f"Телефон: {customer_data.get('phone', 'Не указано')}\n"
        f"Дата рождения: {customer_data.get('birth_date', 'Не указана')}\n"
        f"Баланс: {customer_data.get('balance', 0)}\n"
        f"Роль: {customer_data.get('role', 'Не указана')}"
    )