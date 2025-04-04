import requests
import json
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Базовый URL сервера
BASE_URL = "http://localhost:8000"  # Убедитесь, что адрес правильный


# Загрузка конфигурации
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Файл конфигурации не найден: {config_path}")
        raise SystemExit("Не удалось загрузить конфигурацию. Проверьте файл config.json.")
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле конфигурации: {config_path}")
        raise SystemExit("Некорректный формат файла config.json.")


# Добавление нового клиента
def add_customer(name, phone, birth_date, role="client"):
    url = f"{BASE_URL}/customers/add"
    payload = {
        "phone": phone.strip(),
        "name": name.strip(),
        "birth_date": birth_date.strip(),
        "role": role.strip()  # Добавляем роль
    }
    logger.info(f"Отправка POST-запроса к {url} с данными: {payload}")
    response = requests.post(url, json=payload)
    logger.info(f"Получен ответ: {response.status_code}, {response.text}")
    if response.status_code != 200:
        raise Exception(response.json().get("detail", "Ошибка при добавлении клиента."))
    return response.json()


# Получение информации о клиенте
def get_customer(phone):
    url = f"{BASE_URL}/customers/{phone.strip()}"
    logger.info(f"Отправка GET-запроса к {url}")
    response = requests.get(url)
    logger.info(f"Получен ответ: {response.status_code}, {response.text}")

    if response.status_code == 404:
        raise Exception("Клиент не найден.")
    elif response.status_code != 200:
        raise Exception(response.json().get("detail", "Ошибка при получении данных клиента."))

    data = response.json()
    if "customer" not in data or "transactions" not in data:
        raise Exception("Некорректный формат ответа сервера.")

    return data


# Пополнение баланса
def add_bonus(phone, amount):
    url = f"{BASE_URL}/transactions/add-bonus"
    payload = {"phone": phone.strip(), "amount": float(amount)}
    logger.info(f"Отправка POST-запроса к {url} с данными: {payload}")
    response = requests.post(url, json=payload)
    logger.info(f"Получен ответ: {response.status_code}, {response.text}")
    if response.status_code != 200:
        raise Exception(response.json().get("detail", "Ошибка при пополнении бонусов."))
    return response.json()


# Списание баланса
def deduct_bonus(phone, amount):
    url = f"{BASE_URL}/transactions/deduct-bonus"
    payload = {"phone": phone.strip(), "amount": float(amount)}
    logger.info(f"Отправка POST-запроса к {url} с данными: {payload}")
    response = requests.post(url, json=payload)
    logger.info(f"Получен ответ: {response.status_code}, {response.text}")
    if response.status_code != 200:
        raise Exception(response.json().get("detail", "Ошибка при списании бонусов."))
    return response.json()


# Получение списка клиентов
def list_customers():
    url = f"{BASE_URL}/customers"
    logger.info(f"Отправка GET-запроса к {url}")
    response = requests.get(url)
    logger.info(f"Получен ответ: {response.status_code}, {response.text}")
    if response.status_code != 200:
        raise Exception(response.json().get("detail", "Ошибка при получении списка клиентов."))
    return response.json().get("customers", [])