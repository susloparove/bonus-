import os
import json
import logging
from telebot import TeleBot
from bot.setup_handlers import setup_all_handlers


# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Загрузка токена из config.json
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
        BOT_TOKEN = config.get("telegram_bot_token")
        if not BOT_TOKEN:
            raise ValueError("Отсутствует telegram_bot_token в config.json")
except Exception as e:
    logging.error(f"Ошибка загрузки конфигурации: {e}")
    raise SystemExit("Бот не может быть запущен без токена.")

# Инициализация бота
tbot = TeleBot(BOT_TOKEN)

# Точка входа
if __name__ == "__main__":
    logging.info("Запуск бота...")
    setup_all_handlers(tbot)
    try:
        tbot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")