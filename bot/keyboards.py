from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def password_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton("7", callback_data="password_7"),
        InlineKeyboardButton("8", callback_data="password_8"),
        InlineKeyboardButton("9", callback_data="password_9"),
        InlineKeyboardButton("4", callback_data="password_4"),
        InlineKeyboardButton("5", callback_data="password_5"),
        InlineKeyboardButton("6", callback_data="password_6"),
        InlineKeyboardButton("1", callback_data="password_1"),
        InlineKeyboardButton("2", callback_data="password_2"),
        InlineKeyboardButton("3", callback_data="password_3"),
        InlineKeyboardButton("Отмена", callback_data="password_cancel"),
        InlineKeyboardButton("0", callback_data="password_0"),
        InlineKeyboardButton("Готово", callback_data="password_done")
    ]
    markup.add(*buttons)
    return markup


def numeric_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    # Верхние ряды: 7 8 9 / 4 5 6 / 1 2 3
    keyboard.row(
        types.InlineKeyboardButton("7", callback_data="num_7"),
        types.InlineKeyboardButton("8", callback_data="num_8"),
        types.InlineKeyboardButton("9", callback_data="num_9"),
    )
    keyboard.row(
        types.InlineKeyboardButton("4", callback_data="num_4"),
        types.InlineKeyboardButton("5", callback_data="num_5"),
        types.InlineKeyboardButton("6", callback_data="num_6"),
    )
    keyboard.row(
        types.InlineKeyboardButton("1", callback_data="num_1"),
        types.InlineKeyboardButton("2", callback_data="num_2"),
        types.InlineKeyboardButton("3", callback_data="num_3"),
    )

    # Последний ряд: Отмена, 0, Готово
    keyboard.row(
        types.InlineKeyboardButton("⏪ Отмена", callback_data="num_cancel"),
        types.InlineKeyboardButton("0", callback_data="num_0"),
        types.InlineKeyboardButton("✅ Ввод", callback_data="num_done"),
    )

    return keyboard


def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Добавить клиента", "Инфо о клиенте")
    markup.row("Пополнить", "Списать")
    markup.row("Сменить клиента", "Все клиенты")
    markup.row("Инфо о клиенте", "Поделиться с клиентом")
    markup.row("Выход")
    return markup


def seller_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Пополнить", "Списать")
    markup.row("Инфо о клиенте", "Поделиться с клиентом")
    markup.row("Выход")
    return markup
