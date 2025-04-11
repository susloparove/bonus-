import telebot
from telebot import types
import requests
import json
import os
from datetime import datetime
from typing import Optional
import logging
from colorama import init, Fore

# Инициализация цветов для Windows
init(autoreset=True)

# Настройка логирования
logger = logging.getLogger('BonusBot')
logger.setLevel(logging.DEBUG)


# Форматирование с цветами
class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.RED
        }.get(record.levelname, Fore.WHITE)
        return f"{color}{super().format(record)}"


console_handler = logging.StreamHandler()
console_handler.setFormatter(ColorFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


# Конфигурация
def load_config():
    try:
        with open('../config.json', 'r') as f:
            config = json.load(f)
            logger.info("Конфиг загружен")
            return config
    except FileNotFoundError:
        logger.error("Создайте config.json по образцу config.json.example")
        exit(1)


config = load_config()
BASE_URL = config['base_url']

# Проверка сервера
try:
    requests.get(f"{BASE_URL}/docs", timeout=3)
    logger.info("Сервер доступен")
except requests.exceptions.RequestException as e:
    logger.error(f"Сервер недоступен: {e}")
    exit(1)

# Инициализация бота
bot = telebot.TeleBot(config['telegram_bot_token'])
user_states = {}


class UserState:
    def __init__(self):
        self.phone: Optional[str] = None
        self.current_action: Optional[str] = None


# Вспомогательные функции
def validate_phone(phone: str) -> bool:
    return phone.isdigit() and len(phone) == 11


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False


def format_client_info(data: dict) -> str:
    total = sum(t['amount'] if t['type'] == 'deposit' else -t['amount']
                for t in data.get('transactions', []))

    return (f"*Имя:* {data['name']}\n"
            f"*Телефон:* {data['phone']}\n"
            f"*Дата рождения:* {data['birth_date']}\n"
            f"*Бонусы:* {total}\n\n"
            "Транзакции:\n" +
            "\n".join([f"- {t['type']} {t['amount']} ({t['timestamp'][:10]})"
                       for t in data.get('transactions', [])]))


# Главное меню с кнопкой "Сменить клиента"
def show_main_menu(chat_id: int):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("Информация", callback_data="info"),
        types.InlineKeyboardButton("Пополнить", callback_data="add_bonus"),
        types.InlineKeyboardButton("Списать", callback_data="deduct_bonus"),
        types.InlineKeyboardButton("Добавить клиента", callback_data="add_client"),
        types.InlineKeyboardButton("🔄 Сменить клиента", callback_data="change_client")
    ]
    markup.add(*buttons)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)


# Обработчик /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    user_states[chat_id] = UserState()
    bot.send_message(chat_id, "Введите номер телефона клиента (11 цифр):")
    logger.info(f"Пользователь {chat_id} начал сессию")


# Обработчик ввода номера телефона
@bot.message_handler(func=lambda msg: msg.chat.id in user_states)
def handle_input(message):
    chat_id = message.chat.id
    state = user_states[chat_id]

    # Если нужно сменить клиента
    if state.current_action == 'change_client':
        state.phone = None
        state.current_action = None

    # Ввод номера телефона
    if not state.phone:
        phone = message.text.strip().replace('+', '')
        if not validate_phone(phone):
            bot.reply_to(message, "❌ Неверный формат номера. Введите 11 цифр:")
            return
        state.phone = phone
        logger.info(f"Пользователь {chat_id} выбрал клиента: {phone}")
        show_main_menu(chat_id)
        return

    # Обработка операций
    if state.current_action == 'add_client':
        process_add_client(message)
    elif state.current_action in ('add_bonus', 'deduct_bonus'):
        process_bonus(message)


# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    state = user_states.get(chat_id)

    if not state:
        bot.send_message(chat_id, "Сессия истекла. Нажмите /start")
        return

    try:
        if call.data == "info":
            response = requests.get(f"{BASE_URL}/customers/{state.phone}")

            if response.status_code == 200:
                bot.send_message(chat_id, format_client_info(response.json()), parse_mode='Markdown')
            elif response.status_code == 404:
                bot.send_message(chat_id, "❌ Клиент не найден")
                logger.warning(f"Клиент {state.phone} не найден (chat_id: {chat_id})")
                state.phone = None  # Сбрасываем клиента
                bot.send_message(chat_id, "Введите новый номер телефона:")
            else:
                bot.send_message(chat_id, f"Ошибка сервера: {response.status_code}")

        elif call.data in ("add_bonus", "deduct_bonus"):
            state.current_action = call.data
            action = "пополнения" if call.data == "add_bonus" else "списания"
            bot.send_message(chat_id, f"Введите сумму для {action}:")
            logger.info(f"Пользователь {chat_id} начал операцию {action}")

        elif call.data == "add_client":
            state.current_action = "add_client"
            bot.send_message(chat_id, "Введите данные клиента:\nИмя Фамилия, Телефон, Дата (ДД/ММ/ГГГГ)")

        elif call.data == "change_client":
            state.phone = None
            state.current_action = None
            bot.send_message(chat_id, "Введите новый номер телефона:")
            logger.info(f"Пользователь {chat_id} сменил клиента")

        # После обработки кнопки возвращаемся в главное меню, если не требуется ввод
        if call.data not in ("add_bonus", "deduct_bonus", "add_client"):
            show_main_menu(chat_id)

    except Exception as e:
        logger.error(f"Ошибка при обработке кнопки: {e}")
        bot.send_message(chat_id, "Что-то пошло не так")


# Обработка операций с бонусами
def process_bonus(message):
    chat_id = message.chat.id
    state = user_states[chat_id]

    try:
        amount = float(message.text)
        endpoint = 'add_bonus' if state.current_action == 'add_bonus' else 'deduct_bonus'
        url = f"{BASE_URL}/customers/{state.phone}/{endpoint}"
        response = requests.post(url, json={"amount": amount})

        if response.status_code == 200:
            bot.send_message(chat_id, "✅ Операция выполнена успешно")
        elif response.status_code == 404:
            bot.send_message(chat_id, "❌ Клиент не найден")
            state.phone = None  # Сбрасываем клиента
            bot.send_message(chat_id, "Введите новый номер телефона:")
        else:
            bot.send_message(chat_id, f"Ошибка: {response.status_code}")

    except ValueError:
        bot.send_message(chat_id, "❌ Введите корректное число")
    except Exception as e:
        logger.error(f"Ошибка операции: {e}")
        bot.send_message(chat_id, "Ошибка при выполнении операции")
    finally:
        state.current_action = None


# Обработка добавления клиента
def process_add_client(message):
    chat_id = message.chat.id
    state = user_states[chat_id]

    try:
        parts = message.text.split(',')
        if len(parts) != 3:
            raise ValueError

        name, phone, birth_date = (p.strip() for p in parts)

        if not validate_phone(phone):
            raise ValueError("Неверный номер телефона")
        if not validate_date(birth_date):
            raise ValueError("Неверная дата")

        response = requests.post(f"{BASE_URL}/customers", json={
            "name": name,
            "phone": phone,
            "birth_date": birth_date
        })

        if response.status_code == 200:
            bot.send_message(chat_id, "✅ Клиент добавлен")
        elif response.status_code == 400:
            bot.send_message(chat_id, "❌ Клиент уже существует")
        else:
            raise Exception(f"Ошибка сервера: {response.status_code}")

    except ValueError as e:
        bot.send_message(chat_id, f"❌ Ошибка ввода: {e}")
    except Exception as e:
        logger.error(f"Ошибка добавления клиента: {e}")
        bot.send_message(chat_id, "Ошибка при добавлении клиента")
    finally:
        state.current_action = None


if __name__ == '__main__':
    logger.info("Бот запущен")
    bot.polling(none_stop=True)