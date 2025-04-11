from telebot import TeleBot
from bot.handlers.auth import register_auth_handlers
from bot.handlers.transaction import register_transaction_handlers
from bot.handlers.menu import register_menu_handlers

def setup_all_handlers(bot: TeleBot):
    register_auth_handlers(bot)
    register_transaction_handlers(bot)
    register_menu_handlers(bot)
