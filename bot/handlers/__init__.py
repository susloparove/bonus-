from telebot import TeleBot

from bot.handlers.auth import register_auth_handlers
from bot.handlers.transaction import register_transaction_handlers
from bot.handlers.menu import register_menu_handlers
from bot.handlers.customer import register_customer_handlers


def register_all_handlers(tbot: TeleBot):
    register_auth_handlers(tbot)
    register_customer_handlers(tbot)
    register_transaction_handlers(tbot)
    register_menu_handlers(tbot)
