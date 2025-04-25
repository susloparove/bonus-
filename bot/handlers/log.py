# bot/handlers/log.py

from telebot import TeleBot
from bot.handlers.auth import AUTHORIZED_USERS
from server.users import get_user_role
import os
import json

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "actions.json")


def register_log_handlers(tbot: TeleBot):
    @tbot.message_handler(func=lambda msg: msg.text == "📄 Журнал действий")
    def handle_show_log(message):
        chat_id = message.chat.id
        username = AUTHORIZED_USERS.get(chat_id)

        if not username or get_user_role(username) != "admin":
            tbot.send_message(chat_id, "❌ Только администратор может просматривать лог.")
            return

        if not os.path.exists(LOG_PATH):
            tbot.send_message(chat_id, "📭 Журнал пуст.")
            return

        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)

            if not logs:
                tbot.send_message(chat_id, "📭 Журнал пуст.")
                return

            # Покажем только последние 10 записей
            last_logs = logs[-10:]
            text = "<b>📄 Последние действия:</b>\n\n"
            for entry in last_logs:
                text += (
                    f"🕒 {entry['timestamp']}\n"
                    f"👤 {entry['user']} — {entry['action']}\n"
                    f"📱 Клиент: {entry['target']}, 💰 {entry['amount'] or '-'}₽\n\n"
                )

            tbot.send_message(chat_id, text.strip(), parse_mode="HTML")
        except Exception as e:
            tbot.send_message(chat_id, f"❌ Ошибка при чтении лога: {e}")
