from telebot import TeleBot, types
from bot.utils import validate_birth_date
from .auth import user_data, current_client_phone  # добавили current_client_phone
from server.customers import get_customer_info, add_customer, list_customers

def register_customer_handlers(tbot: TeleBot):

    @tbot.message_handler(func=lambda msg: msg.text == "Добавить клиента")
    @tbot.message_handler(commands=['add'])
    def handle_add_customer(message: types.Message):
        tbot.send_message(message.chat.id, "Введите имя клиента:")
        tbot.register_next_step_handler(message, lambda m: process_name(m, tbot))

    def process_name(message: types.Message, tbot: TeleBot):
        user_data[message.chat.id] = {'name': message.text}
        tbot.send_message(message.chat.id, "Введите номер телефона:")
        tbot.register_next_step_handler(message, lambda m: process_phone(m, tbot))

    def process_phone(message: types.Message, tbot: TeleBot):
        user_data[message.chat.id]['phone'] = message.text
        tbot.send_message(message.chat.id, "Введите дату рождения (дд.мм.гггг):")
        tbot.register_next_step_handler(message, lambda m: process_birth_date(m, tbot))

    def process_birth_date(message: types.Message, tbot: TeleBot):
        birth_date = message.text.strip()
        if not validate_birth_date(birth_date):
            tbot.send_message(message.chat.id, "❌ Неверный формат даты. Попробуйте снова:")
            tbot.register_next_step_handler(message, lambda m: process_birth_date(m, tbot))
            return

        data = user_data[message.chat.id]
        phone = data["phone"]
        name = data["name"]

        try:
            # ✅ Добавляем клиента
            add_customer(phone, name, birth_date)

            # ✅ Устанавливаем текущего клиента
            current_client_phone[message.chat.id] = phone

            # Получаем актуальную информацию
            info = get_customer_info(phone)
            tbot.send_message(
                message.chat.id,
                f"Клиент добавлен ✅\n"
                f"👤 {info['name']}\n"
                f"📞 {phone}\n"
                f"💰 Баланс: {info['balance']}₿\n\n"
                f"✅ Вы работаете с этим клиентом."
            )
        except Exception as e:
            tbot.send_message(message.chat.id, f"❌ Ошибка при добавлении клиента: {e}")

    @tbot.message_handler(commands=['list'])
    def handle_list_customers(message: types.Message):
        try:
            result = list_customers()
            if not result["customers"]:
                tbot.send_message(message.chat.id, "Список клиентов пуст.")
                return

            response = "\n".join(result["customers"])
            tbot.send_message(message.chat.id, f"📋 Клиенты:\n{response}")
        except Exception as e:
            tbot.send_message(message.chat.id, f"❌ Ошибка при получении списка: {e}")

    @tbot.message_handler(commands=['find'])
    def handle_find_customer(message: types.Message):
        tbot.send_message(message.chat.id, "Введите номер телефона клиента:")
        tbot.register_next_step_handler(message, lambda m: process_find_customer(m, tbot))

    def process_find_customer(message: types.Message, tbot: TeleBot):
        phone = message.text.strip()
        try:
            info = get_customer_info(phone)
            msg = (f"👤 Имя: {info['name']}\n"
                   f"📞 Телефон: {phone}\n"
                   f"💰 Баланс: {info['balance']}₿")
        except Exception as e:
            msg = f"❌ Ошибка: {e}"
        tbot.send_message(message.chat.id, msg)
