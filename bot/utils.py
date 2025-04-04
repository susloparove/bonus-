import sys
import os
import requests
import json
import logging

# Добавляем корень проекта в пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импорт общего конфига
try:
    from config import SERVER_HOST, SERVER_PORT
except ImportError:
    logging.error("Не удалось загрузить настройки сервера. Проверьте файл config.py.")
    raise SystemExit("Ошибка загрузки конфигурации.")

# Базовый URL сервера
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Пример функции для запроса к серверу
def add_customer(name, phone, birth_date, role="client"):
    url = f"{BASE_URL}/customers/add"
    payload = {
        "phone": phone.strip(),
        "name": name.strip(),
        "birth_date": birth_date.strip(),
        "role": role.strip()
    }
    logger.info(f"Отправка POST-запроса к {url} с данными: {payload}")
    response = requests.post(url, json=payload)
    logger.info(f"Получен ответ: {response.status_code}, {response.text}")
    if response.status_code != 200:
        raise Exception(response.json().get("detail", "Ошибка при добавлении клиента."))
    return response.json()