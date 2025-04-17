# bot/utils.py
from datetime import datetime
from bot.handlers.auth import current_client_phone  # ← Импорт здесь, не внутри функции

def validate_phone(phone: str) -> bool:
    return phone.isdigit() and len(phone) == 11 and phone.startswith("7")


def validate_birth_date(birth_date: str) -> bool:
    try:
        datetime.strptime(birth_date, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def format_customer_info(customer_info: dict, phone: str) -> str:
    customer = customer_info.get("customer", {})
    transactions = customer_info.get("transactions", [])

    lines = [
        f"📞 Телефон: {phone}",
        f"👤 Имя: {customer.get('name', '-')}",
        f"🎂 Дата рождения: {customer.get('birth_date', '-')}",
        f"💰 Баланс: {customer.get('balance', 0)}₿",
        "",
        "📜 Транзакции:"
    ]

    if not transactions:
        lines.append("Нет транзакций.")
    else:
        for t in transactions:
            lines.append(f"{t['timestamp']}: {t['type']} {t['amount']}₿")

    return "\n".join(lines)

import qrcode
from io import BytesIO

def generate_deep_link(phone: str) -> str:
    return f"https://t.me/Tg_Chat1969_Bot?start={phone}"

def generate_qr_image(link: str) -> BytesIO:
    img = qrcode.make(link)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

