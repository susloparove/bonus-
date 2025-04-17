from telebot import TeleBot
from bot.handlers.auth import register_auth_handlers
from bot.handlers.transaction import register_transaction_handlers
from bot.handlers.menu import register_menu_handlers, register_client_info_handler
from bot.handlers.customer import register_customer_handlers  # ✅ ДОБАВЛЕНО

def setup_all_handlers(tbot: TeleBot):
    register_auth_handlers(tbot)
    register_transaction_handlers(tbot)
    register_menu_handlers(tbot)
    register_customer_handlers(tbot)  # ✅ ДОБАВЛЕНО
    register_client_info_handler(tbot)