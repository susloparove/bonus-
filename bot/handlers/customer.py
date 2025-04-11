from telebot import TeleBot, types
from bot.utils import validate_birth_date
from .auth import user_data, clients


def register_customer_handlers(tbot: TeleBot):
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
        birth_date = message.text
        if not validate_birth_date(birth_date):
            tbot.send_message(message.chat.id, "Неверный формат даты. Попробуйте снова:")
            tbot.register_next_step_handler(message, lambda m: process_birth_date(m, tbot))
            return

        user_data[message.chat.id]['birth_date'] = birth_date
        user_data[message.chat.id]['balance'] = 0.0
        clients.append(user_data[message.chat.id])
        tbot.send_message(message.chat.id, "Клиент добавлен ✅")

    @tbot.message_handler(commands=['list'])
    def handle_list_customers(message: types.Message):
        if not clients:
            tbot.send_message(message.chat.id, "Список клиентов пуст.")
            return

        response = ""
        for c in clients:
            response += f"👤 {c['name']} | 📞 {c['phone']} | 💰 {c['balance']}₽\n"
        tbot.send_message(message.chat.id, response)

    @tbot.message_handler(commands=['find'])
    def handle_find_customer(message: types.Message):
        tbot.send_message(message.chat.id, "Введите номер телефона клиента:")
        tbot.register_next_step_handler(message, lambda m: process_find_customer(m, tbot))

    def process_find_customer(message: types.Message, tbot: TeleBot):
        phone = message.text.strip()
        found = next((c for c in clients if c['phone'] == phone), None)

        if found:
            msg = (f"👤 Имя: {found['name']}\n"
                   f"📞 Телефон: {found['phone']}\n"
                   f"🎂 Дата рождения: {found['birth_date']}\n"
                   f"💰 Баланс: {found['balance']}₽")
        else:
            msg = "Клиент с таким номером не найден ❌"
        tbot.send_message(message.chat.id, msg)
