import logging
from telebot import types
from bot.keyboards import (
    main_menu_keyboard, numeric_keyboard, password_keyboard, role_keyboard, seller_menu_keyboard
)
from bot.utils import (
    add_customer, get_customer, add_bonus, deduct_bonus, list_customers
)
from server.users import authenticate_user, get_user_role

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

AUTHORIZED_USERS = {}  # Хранит текущих авторизованных пользователей (chat_id: username)
user_password_input = {}  # Хранит текущий пароль пользователя
user_input = {}  # Хранит текущий ввод пользователя (например, номер телефона или сумму)

def setup_handlers(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        chat_id = message.chat.id
        AUTHORIZED_USERS.pop(chat_id, None)  # Сбрасываем авторизацию
        user_password_input[chat_id] = ""  # Очищаем ввод пароля
        bot.send_message(
            message.chat.id,
            "Введите пароль (нажмите 'Готово' после ввода):",
            reply_markup=password_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("password_"))
    def handle_password(call):
        chat_id = call.message.chat.id
        action = call.data.split("_")[1]

        if action == "cancel":
            AUTHORIZED_USERS.pop(chat_id, None)
            user_password_input.pop(chat_id, None)
            bot.edit_message_text(
                "Ввод пароля отменён.",
                chat_id,
                call.message.message_id,
                reply_markup=None
            )
            show_main_menu(call.message)
        elif action == "done":
            password = user_password_input.get(chat_id, "")
            if not password:
                bot.answer_callback_query(call.id, "Пароль не введён.")
                return

            try:
                # Проверяем пароль через authenticate_user
                username = authenticate_user_by_password(password)
                AUTHORIZED_USERS[chat_id] = username  # Сохраняем имя пользователя
                role = get_user_role(username)  # Получаем роль пользователя
                bot.edit_message_text(
                    f"Авторизация успешна! Ваша роль: {role}",
                    chat_id,
                    call.message.message_id,
                    reply_markup=None
                )
                show_main_menu(call.message)
            except ValueError as e:
                bot.answer_callback_query(call.id, str(e))
                bot.edit_message_text(
                    "Неверный пароль. Попробуйте снова:",
                    chat_id,
                    call.message.message_id,
                    reply_markup=password_keyboard()
                )
        else:
            user_password_input[chat_id] += action
            bot.answer_callback_query(call.id, "Символ добавлен.")

    @bot.message_handler(func=lambda message: message.text == "Добавить клиента")
    def handle_add_client(message):
        chat_id = message.chat.id
        username = AUTHORIZED_USERS.get(chat_id)
        if not username:
            bot.send_message(chat_id, "Вы не авторизованы. Введите пароль для авторизации:")
            return

        bot.send_message(
            chat_id,
            "Введите имя клиента:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, process_first_name)

    def process_first_name(message):
        first_name = message.text.strip()
        bot.send_message(
            message.chat.id,
            "Введите фамилию клиента:"
        )
        bot.register_next_step_handler(message, process_last_name, first_name)

    def process_last_name(message, first_name):
        last_name = message.text.strip()
        bot.send_message(
            message.chat.id,
            "Введите дату рождения клиента в формате ДДММГГГГ:"
        )
        bot.register_next_step_handler(message, process_birth_date, first_name, last_name)

    def process_birth_date(message, first_name, last_name):
        birth_date = message.text.strip()
        if len(birth_date) != 8 or not birth_date.isdigit():
            bot.send_message(
                message.chat.id,
                "Некорректный формат даты рождения. Введите дату в формате ДДММГГГГ:"
            )
            bot.register_next_step_handler(message, process_birth_date, first_name, last_name)
            return

        bot.send_message(
            message.chat.id,
            "Выберите роль клиента:",
            reply_markup=role_keyboard()
        )
        bot.register_next_step_handler(message, process_role, first_name, last_name, birth_date)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
    def process_role(call):
        first_name = call.message.text.split(":")[1].strip()
        last_name = call.message.text.split(":")[2].strip()
        birth_date = call.message.text.split(":")[3].strip()
        role = call.data.split("_")[1]
        full_name = f"{first_name} {last_name}"
        phone = "79000000000"  # Пример номера телефона (можно запросить дополнительно)

        try:
            response = add_customer(full_name, phone, birth_date, role)
            bot.send_message(
                call.message.chat.id,
                f"Клиент успешно добавлен:\nФИО: {full_name}\nДата рождения: {birth_date}\nРоль: {role}",
                reply_markup=main_menu_keyboard()
            )
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка: проверьте формат ввода ({e}).")
    @bot.message_handler(func=lambda message: message.text == "Пополнить")
    def handle_top_up(message):
        chat_id = message.chat.id
        username = AUTHORIZED_USERS.get(chat_id)
        if not username:
            bot.send_message(chat_id, "Вы не авторизованы. Введите пароль для авторизации:")
            return

        user_input[chat_id] = ""  # Инициализируем пустой ввод
        bot.send_message(
            chat_id,
            "Введите номер телефона клиента в формате 79ХХХХХХХХХ:",
            reply_markup=numeric_keyboard()
        )

    @bot.message_handler(func=lambda message: message.text == "Списать")
    def handle_deduct(message):
        chat_id = message.chat.id
        username = AUTHORIZED_USERS.get(chat_id)
        if not username:
            bot.send_message(chat_id, "Вы не авторизованы. Введите пароль для авторизации:")
            return

        user_input[chat_id] = ""  # Инициализируем пустой ввод
        bot.send_message(
            chat_id,
            "Введите номер телефона клиента в формате 79ХХХХХХХХХ:",
            reply_markup=numeric_keyboard()
        )

    @bot.message_handler(func=lambda message: message.text == "Все клиенты")
    def handle_list_clients(message):
        try:
            customers = list_customers()
            if not customers:
                bot.send_message(message.chat.id, "Нет зарегистрированных клиентов.")
            else:
                client_list = "\n".join(customers)
                bot.send_message(message.chat.id, f"Список клиентов:\n{client_list}")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при получении списка клиентов: {e}")

    @bot.message_handler(func=lambda message: message.text == "Закрыть клиента")
    def handle_close_client(message):
        chat_id = message.chat.id
        AUTHORIZED_USERS.pop(chat_id, None)
        user_input.pop(chat_id, None)
        bot.send_message(
            chat_id,
            "Работа с клиентом завершена.",
            reply_markup=main_menu_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("num_"))
    def handle_numeric_input(call):
        chat_id = call.message.chat.id
        action = call.data.split("_")[1]

        if action == "cancel":
            user_input.pop(chat_id, None)
            bot.edit_message_text(
                "Ввод отменён.",
                chat_id,
                call.message.message_id,
                reply_markup=None
            )
            show_main_menu(call.message)
        elif action == "done":
            input_value = user_input.get(chat_id, "")
            if not input_value:
                bot.answer_callback_query(call.id, "Ничего не введено.")
                return

            if len(input_value) == 11 and input_value.startswith("7"):
                global current_client_phone
                current_client_phone = input_value
                try:
                    customer_info = get_customer(input_value)
                    info = format_customer_info(customer_info)
                    bot.edit_message_text(
                        f"Клиент выбран:\n{info}",
                        chat_id,
                        call.message.message_id,
                        reply_markup=main_menu_keyboard()
                    )
                except Exception as e:
                    bot.edit_message_text(
                        "Клиент не найден. Хотите добавить нового клиента?",
                        chat_id,
                        call.message.message_id,
                        reply_markup=main_menu_keyboard()
                    )
            else:
                try:
                    amount = float(input_value)
                    operator = AUTHORIZED_USERS.get(chat_id)  # Получаем имя оператора
                    response = add_bonus(current_client_phone, amount, operator)
                    update_client_info(call.message, response["balance"])
                    bot.edit_message_text(
                        "Операция выполнена.",
                        chat_id,
                        call.message.message_id,
                        reply_markup=main_menu_keyboard()
                    )
                except ValueError:
                    bot.answer_callback_query(call.id, "Некорректный ввод.")

            user_input.pop(chat_id, None)  # Очищаем ввод
        else:
            user_input[chat_id] = user_input.get(chat_id, "") + action
            bot.answer_callback_query(call.id, f"Введено: {user_input[chat_id]}")

    def show_main_menu(message):
        chat_id = message.chat.id
        username = AUTHORIZED_USERS.get(chat_id)
        if not username:
            bot.send_message(
                chat_id,
                "Вы не авторизованы. Введите пароль для авторизации:",
                reply_markup=password_keyboard()
            )
            return

        role = get_user_role(username)
        if role == "admin":
            # Главное меню для администратора
            bot.send_message(
                chat_id,
                f"Выберите действие (Администратор: {username}):",
                reply_markup=main_menu_keyboard()
            )
        elif role == "seller":
            # Главное меню для продавца
            bot.send_message(
                chat_id,
                f"Выберите действие (Продавец: {username}):",
                reply_markup=seller_menu_keyboard()
            )
        else:
            bot.send_message(
                chat_id,
                "Неизвестная роль. Обратитесь к администратору."
            )

    def update_client_info(message, balance):
        try:
            customer_info = get_customer(current_client_phone)
            info = format_customer_info(customer_info)
            bot.send_message(
                message.chat.id,
                f"Транзакция выполнена. Текущая информация о клиенте:\n{info}",
                reply_markup=main_menu_keyboard()
            )
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при обновлении информации: {e}")

def format_customer_info(customer_info):
    customer = customer_info["customer"]
    transactions = customer_info["transactions"]
    transaction_types = {"add": "Пополнение", "deduct": "Списание"}
    transactions_str = "\n".join(
        [f"{transaction_types.get(t['type'], t['type'])}: {t['amount']} ({t['timestamp']})" for t in transactions]
    )
    return (
        f"Телефон: {current_client_phone}\n"
        f"ФИО: {customer['name']}\n"
        f"Дата рождения: {customer['birth_date']}\n"
        f"Баланс: {customer['balance']}\n"
        f"Транзакции:\n{transactions_str or 'Нет транзакций'}"
    )

# Вспомогательная функция для проверки пароля
def authenticate_user_by_password(password):
    """
    Проверяет пароль и возвращает имя пользователя.
    :param password: Введённый пароль
    :return: Имя пользователя, если аутентификация успешна
    """
    try:
        users = load_users()  # Загружаем всех пользователей
        for username, data in users.items():
            stored_password_hash = data["password"].encode("utf-8")
            if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
                return username
        raise ValueError("Неверное имя пользователя или пароль.")
    except Exception as e:
        raise ValueError("Ошибка при аутентификации.")