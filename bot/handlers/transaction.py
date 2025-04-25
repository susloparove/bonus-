from telebot import TeleBot, types
from server.transactions import add_bonus, deduct_bonus
from server.customers import get_customer
from bot.keyboards import numeric_keyboard, main_menu_keyboard
from bot.utils import validate_phone
from bot.handlers.auth import AUTHORIZED_USERS, user_input, current_client_phone, current_action
from bot.handlers.menu import show_short_customer_info


def register_transaction_handlers(tbot: TeleBot):

    @tbot.message_handler(func=lambda msg: msg.text in ["Пополнить", "Списать"])
    def handle_money_operation(message: types.Message):
        chat_id = message.chat.id

        if chat_id not in AUTHORIZED_USERS:
            tbot.send_message(chat_id, "Вы не авторизованы.")
            return

        current_action[chat_id] = "add" if message.text == "Пополнить" else "deduct"
        phone = current_client_phone.get(chat_id)

        if phone:
            show_short_customer_info(chat_id, tbot, phone)
            tbot.send_message(chat_id, f"Введите сумму для клиента {phone}:")
            tbot.register_next_step_handler_by_chat_id(
                chat_id,
                lambda m: process_amount(m, tbot, phone)
            )
        else:
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
            try:
                tbot.edit_message_text(
                    f"Текущий ввод: {user_input[chat_id]}",
                    chat_id,
                    call.message.message_id,
                    reply_markup=numeric_keyboard()
                )
            except Exception:
                pass

        elif action == "cancel":
            user_input.pop(chat_id, None)
            current_action.pop(chat_id, None)
            tbot.send_message(chat_id, "Ввод отменён.", reply_markup=main_menu_keyboard())

        elif action == "done":
            phone = user_input.pop(chat_id, "").strip()
            if not validate_phone(phone):
                tbot.edit_message_text(
                    "Некорректный номер телефона. Попробуйте снова.",
                    chat_id,
                    call.message.message_id,
                    reply_markup=numeric_keyboard()
                )
                return

            current_client_phone[chat_id] = phone
            show_short_customer_info(chat_id, tbot, phone)

            operation = current_action.get(chat_id)
            if operation == "info":
                current_action.pop(chat_id, None)
                from bot.handlers.menu import show_customer_info
                show_customer_info(chat_id, tbot, phone)
            elif operation in ("add", "deduct"):
                tbot.send_message(chat_id, f"Введите сумму для клиента {phone}:")
                tbot.register_next_step_handler_by_chat_id(
                    chat_id,
                    lambda m: process_amount(m, tbot, phone)
                )
            else:
                tbot.send_message(chat_id, "❌ Неизвестная операция.", reply_markup=main_menu_keyboard())


def process_amount(message: types.Message, tbot: TeleBot, phone: str):
    chat_id = message.chat.id
    operator = AUTHORIZED_USERS.get(chat_id)  # <<< здесь
    if not operator:
        tbot.send_message(chat_id, "❌ Вы не авторизованы.")
        return

    try:
        amount = float(message.text.replace(",", "."))
        operation = current_action.get(chat_id)
        operator = AUTHORIZED_USERS.get(chat_id)  # <<< здесь
        if operation == "add":
            add_bonus(phone, amount, operator)
            tbot.send_message(chat_id, f"💰 Зачислено {amount}₽ клиенту {phone}.")
        elif operation == "deduct":
            deduct_bonus(phone, amount, operator)
            tbot.send_message(chat_id, f"💸 Списано {amount}₽ с клиента {phone}.")
        else:
            tbot.send_message(chat_id, "❌ Неизвестная операция.")
            return

        # после операции можно показать обновлённый баланс
        info = get_customer(phone)["customer"]
        tbot.send_message(chat_id, f"📊 Новый баланс: {info['balance']}₽")
    except Exception as e:
        tbot.send_message(chat_id, f"❌ Ошибка при операции: {e}")

        # ✅ Удаляем текущую операцию
        # current_action.pop(message.chat.id, None)

    except Exception as e:
        tbot.send_message(message.chat.id, f"❌ Ошибка при операции: {e}")
