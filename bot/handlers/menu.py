from telebot import TeleBot, types
from server.customers import list_customers, get_customer
from bot.keyboards import numeric_keyboard, password_keyboard, main_menu_keyboard, client_menu_keyboard
from bot.handlers.auth import AUTHORIZED_USERS, current_client_phone, user_input, current_action, show_main_menu


def register_menu_handlers(tbot: TeleBot):
    @tbot.message_handler(func=lambda msg: msg.text == "Все клиенты")
    def handle_list_customers(message: types.Message):
        chat_id = message.chat.id

        if chat_id not in AUTHORIZED_USERS:
            tbot.send_message(chat_id, "Вы не авторизованы.", reply_markup=password_keyboard())
            return

        try:
            customers = list_customers()
            if not customers["customers"]:
                tbot.send_message(chat_id, "Список клиентов пуст.")
                return

            result = "\n".join(customers["customers"])
            tbot.send_message(chat_id, f"👥 Все клиенты:\n\n{result}")
        except Exception as e:
            tbot.send_message(chat_id, f"❌ Ошибка при получении списка: {e}")

    @tbot.message_handler(func=lambda msg: msg.text == "Инфо о клиенте")
    def handle_customer_info(message: types.Message):
        chat_id = message.chat.id
        phone = current_client_phone.get(chat_id)

        if chat_id not in AUTHORIZED_USERS:
            tbot.send_message(chat_id, "Вы не авторизованы.")
            return

        if not phone:
            current_action[chat_id] = "info"
            user_input[chat_id] = ""
            tbot.send_message(chat_id, "Введите номер клиента:", reply_markup=numeric_keyboard())
            return

        show_customer_info(chat_id, tbot, phone)

    @tbot.message_handler(func=lambda msg: msg.text == "Поделиться")
    def handle_share_client_link(message: types.Message):
        chat_id = message.chat.id
        phone = current_client_phone.get(chat_id)
        if not phone:
            tbot.send_message(chat_id, "❌ Сначала выберите клиента.")
            return

        from bot.utils import generate_deep_link, generate_qr_image

        link = generate_deep_link(phone)
        qr = generate_qr_image(link)

        tbot.send_photo(chat_id, photo=qr, caption=f"🔗 Ссылка для клиента:\n{link}")

    @tbot.message_handler(func=lambda msg: msg.text == "Сменить клиента")
    def handle_change_client(message: types.Message):
        chat_id = message.chat.id
        current_client_phone.pop(chat_id, None)
        current_action.pop(chat_id, None)
        user_input[chat_id] = ""
        tbot.send_message(chat_id, "Введите номер нового клиента:", reply_markup=numeric_keyboard())

    @tbot.message_handler(func=lambda msg: msg.text == "Выход")
    def handle_logout(message: types.Message):
        chat_id = message.chat.id
        AUTHORIZED_USERS.pop(chat_id, None)
        current_client_phone.pop(chat_id, None)
        current_action.pop(chat_id, None)
        user_input.pop(chat_id, None)
        tbot.send_message(chat_id, "🚪 Вы вышли из системы.")
        tbot.send_message(chat_id, "Введите пароль для входа:", reply_markup=password_keyboard())

    @tbot.message_handler(func=lambda msg: msg.text == "Информация")
    def handle_client_info(message: types.Message):
        chat_id = message.chat.id
        phone = AUTHORIZED_USERS.get(chat_id)

        if not phone:
            tbot.send_message(chat_id, "Вы не авторизованы.")
            return

        from server.customers import get_customer
        from bot.utils import format_customer_info
        try:
            info = get_customer(phone)
            text = format_customer_info(info, phone)
            tbot.send_message(chat_id, text)
        except Exception as e:
            tbot.send_message(chat_id, f"❌ Ошибка: {e}")

def show_customer_info(chat_id, bot: TeleBot, phone: str):
    try:
        customer_info = get_customer(phone)
        customer = customer_info["customer"]
        transactions = customer_info["transactions"]

        last_ops = "\n".join([
            f"{'➕' if t['type'] == 'add' else '➖'} {abs(t['amount'])}₽ — {t['timestamp']}"
            for t in transactions
        ]) or "Нет транзакций"

        msg = (
            f"👤 <b>{customer['name']}</b>\n"
            f"📞 Телефон: <code>{phone}</code>\n"
            f"🎂 Дата рождения: {customer['birth_date']}\n"
            f"💰 Баланс: <b>{customer['balance']}₽</b>\n"
            f"\n🧾 Последние транзакции:\n{last_ops}"
        )
        bot.send_message(chat_id, msg, parse_mode="HTML")
        current_client_phone[chat_id] = phone

    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка: {e}")


def show_short_customer_info(chat_id, bot: TeleBot, phone: str):
    try:
        customer = get_customer(phone)["customer"]
        msg = (
            f"👤 Имя: <b>{customer['name']}</b>\n"
            f"🎂 Дата рождения: {customer['birth_date']}\n"
            f"💰 Баланс: <b>{customer['balance']}₽</b>"
        )
        bot.send_message(chat_id, msg, parse_mode="HTML")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка: {e}")

from server.customers import get_customer
from telebot import TeleBot, types
from bot.handlers.auth import current_client_phone

def register_client_info_handler(tbot: TeleBot):
    @tbot.message_handler(func=lambda msg: msg.text == "Информация")
    def handle_client_info(message: types.Message):
        chat_id = message.chat.id
        phone = current_client_phone.get(chat_id)

        if not phone:
            tbot.send_message(chat_id, "⚠️ Клиент не определён.")
            return

        try:
            data = get_customer(phone)
            customer = data["customer"]
            transactions = data["transactions"]

            msg = (
                f"👤 <b>{customer['name']}</b>\n"
                f"📞 Телефон: <code>{phone}</code>\n"
                f"🎂 Дата рождения: {customer.get('birth_date', '—')}\n"
                f"💰 Баланс: <b>{customer.get('balance', 0)}₽</b>\n"
                f"\n🧾 <b>Транзакции:</b>\n"
            )

            if not transactions:
                msg += "Нет транзакций."
            else:
                for t in transactions:
                    sign = "➕" if t["type"] == "add" else "➖"
                    msg += f"{sign} {abs(t['amount'])}₽ — {t['timestamp']}\n"

            tbot.send_message(chat_id, msg, parse_mode="HTML")
        except Exception as e:
            tbot.send_message(chat_id, f"❌ Ошибка: {e}")
