# bot/utils.py
from datetime import datetime


def validate_phone(phone: str) -> bool:
    """
    Проверяет, что номер телефона состоит из 11 цифр и начинается с 7.
    """
    return phone.isdigit() and len(phone) == 11 and phone.startswith("7")


def validate_birth_date(birth_date: str) -> bool:
    """
    Проверяет, что дата рождения имеет формат ДД.ММ.ГГГГ и существует.
    """
    try:
        datetime.strptime(birth_date, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def format_customer_info(customer_info: dict, phone: str) -> str:
    """
    Форматирует информацию о клиенте для отображения в сообщении.
    """
    customer = customer_info.get("customer", {})
    transactions = customer_info.get("transactions", [])

    lines = [
        f"📞 Телефон: {phone}",
        f"👤 Имя: {customer.get('name', '-')}",
        f"🎂 Дата рождения: {customer.get('birth_date', '-')}",
        f"💰 Баланс: {customer.get('balance', 0)}₽",
        "",
        "📜 Транзакции:"
    ]

    if not transactions:
        lines.append("Нет транзакций.")
    else:
        for t in transactions[-5:]:  # последние 5 транзакций
            lines.append(f"{t['timestamp']}: {t['type']} {t['amount']}₽")

    return "\n".join(lines)
