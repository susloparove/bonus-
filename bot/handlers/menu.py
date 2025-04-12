from telebot import TeleBot, types
from bot.keyboards import numeric_keyboard, password_keyboard, main_menu_keyboard
from server.customers import list_customers
from bot.handlers.auth import AUTHORIZED_USERS, current_client_phone, user_input, show_main_menu

def register_menu_handlers(tbot: TeleBot):
    @tbot.message_handler(func=lambda msg: msg.text == "Все клиенты")
    def handle_list_customers(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in AUTHORIZED_USERS:
            tbot.send_message(chat_id, "Вы не авторизованы.", reply_markup=password_keyboard())
            return
        try:
            customers = list_customers()
            if not customers:
                tbot.send_message(chat_id, "Список клиентов пуст.")
                return

            result = "\n".join([
                f"📞 {phone}: {info['name']} ({info['balance']}₽)"
                for phone, info in customers.items()
            ])
            tbot.send_message(chat_id, f"👥 Клиенты:\n\n{result}")
        except Exception as e:
            tbot.send_message(chat_id, f"❌ Ошибка: {e}")

    @tbot.message_handler(func=lambda msg: msg.text == "Закрыть клиента")
    def handle_close_client(message: types.Message):
        chat_id = message.chat.id
        current_client_phone.pop(chat_id, None)
        user_input.pop(chat_id, None)
        tbot.send_message(chat_id, "🔒 Работа с клиентом завершена.")
        show_main_menu(chat_id, tbot)

    @tbot.message_handler(func=lambda msg: msg.text == "Выход")
    def handle_logout(message: types.Message):
        chat_id = message.chat.id
        AUTHORIZED_USERS.pop(chat_id, None)
        current_client_phone.pop(chat_id, None)
        user_input.pop(chat_id, None)
        tbot.send_message(chat_id, "🚪 Вы вышли из системы.")
        tbot.send_message(chat_id, "Введите пароль для повторного входа:", reply_markup=password_keyboard())

    @tbot.message_handler(commands=['debug'])
    def handle_debug(message: types.Message):
        chat_id = message.chat.id
        auth_user = AUTHORIZED_USERS.get(chat_id, "—")
        client_phone = current_client_phone.get(chat_id, "—")
        current = user_input.get(chat_id, "—")

        debug_msg = (
            f"🛠 <b>Отладочная информация:</b>\n"
            f"👤 Авторизован как: <b>{auth_user}</b>\n"
            f"📞 Текущий клиент: <b>{client_phone}</b>\n"
            f"⌨️ Ввод: <b>{current}</b>"
        )
        tbot.send_message(chat_id, debug_msg, parse_mode="HTML")
