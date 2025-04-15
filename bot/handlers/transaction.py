from server.transactions import add_bonus, deduct_bonus
from server.customers import get_customer_info, get_customer
from telebot import TeleBot, types
from bot.keyboards import numeric_keyboard, main_menu_keyboard
from bot.utils import validate_phone
from bot.handlers.auth import AUTHORIZED_USERS, user_input, current_client_phone, current_action
from bot.handlers.menu import show_customer_info,  show_short_customer_info # если функция там, либо создай рядом


def register_transaction_handlers(tbot: TeleBot):

    @tbot.message_handler(func=lambda msg: msg.text in ["Пополнить", "Списать"])
    def handle_money_operation(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in AUTHORIZED_USERS:
            tbot.send_message(chat_id, "Вы не авторизованы.")
            return

        # Сохраняем текущую операцию
        if message.text == "Пополнить":
            current_action[chat_id] = "add"
        elif message.text == "Списать":
            current_action[chat_id] = "deduct"

        user_input[chat_id] = ""
        tbot.send_message(chat_id, "Введите номер телефона клиента:", reply_markup=numeric_keyboard())

    @tbot.callback_query_handler(func=lambda call: call.data.startswith("num_"))
    def handle_numeric_callback(call: types.CallbackQuery):
        chat_id = call.message.chat.id
        action = call.data.split("_")[1]

        if chat_id not in user_input:
            user_input[chat_id] = ""

        if action.isdigit():
            # Обработка ввода через InlineKeyboardMarkup
            user_input[chat_id] += action
            try:
                tbot.edit_message_text(
                    f"Текущий ввод: {user_input[chat_id]}",
                    chat_id,
                    call.message.message_id,
                    reply_markup=numeric_keyboard()
                )
            except Exception:
                pass  # избегаем ошибки, если сообщение уже изменено
        elif action == "cancel":
            # Отмена ввода
            user_input.pop(chat_id, None)
            current_action.pop(chat_id, None)
            tbot.send_message(chat_id, "Ввод отменён.", reply_markup=main_menu_keyboard())
        elif action == "done":
            # Завершение ввода номера телефона
            phone = user_input.pop(chat_id, "").strip()  # Получаем и очищаем ввод
            if not validate_phone(phone):  # Проверяем корректность номера
                tbot.edit_message_text(
                    "Некорректный номер телефона. Попробуйте снова.",
                    chat_id,
                    call.message.message_id,
                    reply_markup=numeric_keyboard()
                )
                return

            # Сохраняем номер телефона в текущем состоянии
            current_client_phone[chat_id] = phone

            # Показываем краткую информацию о клиенте
            show_short_customer_info(chat_id, tbot, phone)

            # Определяем текущую операцию (add/deduct/info)
            operation = current_action.get(chat_id)
            if operation == "info":
                current_action.pop(chat_id, None)
                show_customer_info(chat_id, tbot, phone)
            elif operation in ("add", "deduct"):
                try:
                    tbot.send_message(
                        chat_id,
                        f"Введите сумму для операции с клиентом {phone}:",
                        reply_markup=numeric_keyboard()
                    )
                except Exception:
                    pass  # избегаем ошибки, если сообщение уже изменено

                tbot.register_next_step_handler_by_chat_id(
                    chat_id,
                    lambda m: process_amount(m, tbot, phone)
                )
            else:
                # Если операция не задана, просто сообщим об этом
                tbot.send_message(
                    chat_id,
                    "❌ Неизвестная операция. Пожалуйста, выберите действие заново.",
                    reply_markup=main_menu_keyboard()
                )
def process_amount(message: types.Message, tbot: TeleBot, phone: str):
    try:
        amount = float(message.text.replace(",", "."))
        operator = AUTHORIZED_USERS.get(message.chat.id)
        if not operator:
            tbot.send_message(message.chat.id, "Вы не авторизованы.")
            return

        # Определяем тип операции из состояния
        operation = current_action.get(message.chat.id)
        if operation == "deduct":
            deduct_bonus(phone, amount, operator)
            success_msg = f"💸 Списано {amount}₽ с клиента {phone}."
        elif operation == "add":
            add_bonus(phone, amount, operator)
            success_msg = f"💰 Зачислено {amount}₽ клиенту {phone}."
        else:
            tbot.send_message(message.chat.id, "❌ Ошибка: Неизвестная операция.")
            return

        # Получаем актуальную информацию
        customer = get_customer_info(phone)
        tbot.send_message(message.chat.id, success_msg + "\n\n" +
                         f"👤 Имя: {customer['name']}\n"
                         f"📞 Телефон: {phone}\n"
                         f"💰 Новый баланс: {customer['balance']}₽")

    except Exception as e:
        tbot.send_message(message.chat.id, f"❌ Ошибка при операции: {e}")
