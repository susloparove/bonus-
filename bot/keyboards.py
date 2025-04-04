from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    """
    Создаёт главное меню с кнопками для администратора.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Добавить клиента"),
        KeyboardButton("Пополнить"),
        KeyboardButton("Списать"),
        KeyboardButton("Все клиенты"),
        KeyboardButton("Закрыть клиента")
    ]
    markup.add(*buttons)
    return markup

def seller_menu_keyboard():
    """
    Создаёт главное меню с кнопками для продавца.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Пополнить"),
        KeyboardButton("Списать"),
        KeyboardButton("Все клиенты"),
        KeyboardButton("Закрыть клиента")
    ]
    markup.add(*buttons)
    return markup

def numeric_keyboard():
    """
    Создаёт цифровую клавиатуру для ввода данных (номер телефона, сумма).
    Использует InlineKeyboardMarkup для избежания автоматической отправки сообщений.
    """
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton("1", callback_data="num_1"),
        InlineKeyboardButton("2", callback_data="num_2"),
        InlineKeyboardButton("3", callback_data="num_3"),
        InlineKeyboardButton("4", callback_data="num_4"),
        InlineKeyboardButton("5", callback_data="num_5"),
        InlineKeyboardButton("6", callback_data="num_6"),
        InlineKeyboardButton("7", callback_data="num_7"),
        InlineKeyboardButton("8", callback_data="num_8"),
        InlineKeyboardButton("9", callback_data="num_9"),
        InlineKeyboardButton("0", callback_data="num_0"),
        InlineKeyboardButton("Отмена", callback_data="num_cancel"),
        InlineKeyboardButton("Готово", callback_data="num_done")
    ]
    markup.add(*buttons)
    return markup

def password_keyboard():
    """
    Создаёт клавиатуру для ввода пароля.
    Использует InlineKeyboardMarkup для скрытия символов пароля.
    """
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton("1", callback_data="password_1"),
        InlineKeyboardButton("2", callback_data="password_2"),
        InlineKeyboardButton("3", callback_data="password_3"),
        InlineKeyboardButton("4", callback_data="password_4"),
        InlineKeyboardButton("5", callback_data="password_5"),
        InlineKeyboardButton("6", callback_data="password_6"),
        InlineKeyboardButton("7", callback_data="password_7"),
        InlineKeyboardButton("8", callback_data="password_8"),
        InlineKeyboardButton("9", callback_data="password_9"),
        InlineKeyboardButton("0", callback_data="password_0"),
        InlineKeyboardButton("Отмена", callback_data="password_cancel"),
        InlineKeyboardButton("Готово", callback_data="password_done")
    ]
    markup.add(*buttons)
    return markup

def role_keyboard():
    """
    Создаёт клавиатуру для выбора роли клиента (Клиент или Пользователь).
    """
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Клиент", callback_data="role_client"),
        InlineKeyboardButton("Пользователь", callback_data="role_user")
    ]
    markup.add(*buttons)
    return markup