from telebot import TeleBot, types
import logging
from bot.keyboards import password_keyboard, main_menu_keyboard, seller_menu_keyboard, client_menu_keyboard
from server.users import authenticate_user_by_password, get_user_role
from server.customers import get_customer

# Глобальные состояния
AUTHORIZED_USERS = {}
user_password_input = {}
user_input = {}
user_data = {}
clients = []
current_client_phone = {}
current_action = {}  # chat_id -> "add" | "deduct" | "info"

# Логирование
logging.basicConfig(level=logging.INFO)


def show_main_menu(chat_id: int, tbot: TeleBot):
    username = AUTHORIZED_USERS.get(chat_id)
    if not username:
        tbot.send_message(chat_id, "Вы не авторизованы.", reply_markup=password_keyboard())
        return

    role = get_user_role(username)
    menu = main_menu_keyboard() if role == "admin" else seller_menu_keyboard()
    tbot.send_message(chat_id, f"Выберите действие ({role.capitalize()}):", reply_markup=menu)


def register_auth_handlers(tbot: TeleBot):
    from fastapi import HTTPException  # добавь вверху

    @tbot.message_handler(commands=['start'])
    def handle_start(message: types.Message):
        chat_id = message.chat.id
        args = message.text.split()

        if len(args) == 2:
            phone = args[1].strip()
            try:
                # Проверим, существует ли клиент
                get_customer(phone)

                # ✅ Авторизуем клиента
                AUTHORIZED_USERS[chat_id] = phone
                current_client_phone[chat_id] = phone

                # Показываем клиентское меню
                tbot.send_message(chat_id, "👋 Добро пожаловать! Вы вошли как клиент.",
                                  reply_markup=client_menu_keyboard())
            except HTTPException:
                tbot.send_message(chat_id, "❌ Клиент с таким номером не найден.")
            except Exception as e:
                tbot.send_message(chat_id, f"❌ Ошибка: {e}")
        else:
            # Запрашиваем пароль только если пользователь не авторизован
            if chat_id not in AUTHORIZED_USERS:
                handle_login(message)

    @tbot.message_handler(commands=['login'])
    def handle_login(message: types.Message):
        chat_id = message.chat.id
        AUTHORIZED_USERS.pop(chat_id, None)
        user_password_input[chat_id] = ""
        tbot.send_message(
            chat_id,
            "Введите пароль (нажмите 'Готово' после ввода):",
            reply_markup=password_keyboard()
        )

    @tbot.callback_query_handler(func=lambda call: call.data.startswith("password_"))
    def handle_password(call: types.CallbackQuery):
        tbot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        action = call.data.split("_")[1]

        if action == "cancel":
            AUTHORIZED_USERS.pop(chat_id, None)
            user_password_input.pop(chat_id, None)
            tbot.edit_message_text("Ввод пароля отменён.", chat_id, call.message.message_id)
            return

        if action == "done":
            password = user_password_input.get(chat_id, "")
            if not password:
                tbot.answer_callback_query(call.id, "Пароль не введён.")
                return

            try:
                username = authenticate_user_by_password(password)
                AUTHORIZED_USERS[chat_id] = username
                role = get_user_role(username)
                tbot.edit_message_text(f"Авторизация успешна, {username}!\nВаша роль: {role}.",
                                       chat_id, call.message.message_id)
                show_main_menu(chat_id, tbot)
            except ValueError:
                user_password_input[chat_id] = ""
                tbot.send_message(
                    chat_id,
                    "Неверный пароль. Повторите ввод:",
                    reply_markup=password_keyboard()
                )
        else:
            user_password_input[chat_id] += action




