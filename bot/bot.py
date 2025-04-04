import json
import logging
import os
from telebot import TeleBot
from bot.handlers import setup_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации из config.json
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
        BOT_TOKEN = config.get("BOT_TOKEN")
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в config.json.")
except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
    logger.error(f"Ошибка загрузки конфигурации: {e}")
    raise SystemExit("Ошибка загрузки конфигурации.")

# Инициализация бота
bot = TeleBot(BOT_TOKEN)

# Настройка обработчиков
setup_handlers(bot)

# Запуск бота
if __name__ == "__main__":
    logger.info("Запуск бота...")
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise SystemExit("Бот остановлен из-за ошибки.")