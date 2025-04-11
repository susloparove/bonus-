
from server.transactions import add_bonus, deduct_bonus
from telebot import TeleBot, types
from bot.keyboards import numeric_keyboard, main_menu_keyboard
from bot.utils import validate_phone
from bot.handlers.auth import AUTHORIZED_USERS, user_input, current_client_phone

# Словарь для хранения текущей операции (пополнение или списание)
current_operation = {}

def register_transaction_handlers(tbot: TeleBot):

    @tbot.message_handler(func=lambda msg: msg.text in ["Пополнить", "Списать"])
    def handle_money_operation(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in AUTHORIZED_USERS:
            tbot.send_message(chat_id, "Вы не авторизованы.")
            return

        # Сохраняем текущую операцию
        if message.text == "Пополнить":
            current_operation[chat_id] = "add"
        elif message.text == "Списать":
            current_operation[chat_id] = "deduct"

        user_input[chat_id] = ""
        tbot.send_message(chat_id, "Введите номер телефона клиента:", reply_markup=numeric_keyboard())

    @tbot.callback_query_handler(func=lambda call: call.data.startswith("num_"))
    def handle_numeric_callback(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        action = call.data.split("_")[1]

        if chat_id not in user_input:
            user_input[chat_id] = ""

        if action.isdigit():
            user_input[chat_id] += action
            tbot.edit_message_text(
                f"Текущий ввод: {user_input[chat_id]}",
                chat_id,
                call.message.message_id,
                reply_markup=numeric_keyboard()
            )
        elif action == "cancel":
            user_input.pop(chat_id, None)
            tbot.edit_message_text(
                "Ввод отменён.",
                chat_id,
                call.message.message_id,
                reply_markup=None
            )
        elif action == "done":
            phone = user_input.pop(chat_id, "")
            if validate_phone(phone):
                current_client_phone[chat_id] = phone
                tbot.edit_message_text(
                    f"Вы ввели номер: {phone}. Введите сумму:",
                    chat_id,
                    call.message.message_id
                )
                tbot.register_next_step_handler_by_chat_id(
                    chat_id,
                    lambda m: process_amount(m, tbot, phone)
                )
            else:
                tbot.edit_message_text(
                    "Некорректный номер телефона. Попробуйте снова.",
                    chat_id,
                    call.message.message_id,
                    reply_markup=numeric_keyboard()
                )

def process_amount(message: types.Message, bot: TeleBot, phone: str):
    try:
        amount = float(message.text.replace(",", "."))
        operator = AUTHORIZED_USERS.get(message.chat.id)
        if not operator:
            bot.send_message(message.chat.id, "Вы не авторизованы.")
            return

        # Определяем тип операции из состояния
        operation = current_operation.get(message.chat.id)
        if operation == "deduct":
            # списание
            deduct_bonus(phone, amount, operator)
            bot.send_message(message.chat.id, f"💸 Списано {amount}₽ с клиента {phone}.")
        elif operation == "add":
            # пополнение
            add_bonus(phone, amount, operator)
            bot.send_message(message.chat.id, f"💰 Зачислено {amount}₽ клиенту {phone}.")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка: Неизвестная операция.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при операции: {e}")