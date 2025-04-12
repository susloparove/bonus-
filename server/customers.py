import json
import os
from datetime import datetime
from fastapi import HTTPException
import logging
from .utils import load_data, save_data

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение пути к корневой директории
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Поднимаемся на уровень выше
DATA_DIR = os.path.join(BASE_DIR, "data")  # Путь к папке data
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")  # Путь к файлу customers.json
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")  # Путь к файлу transactions.json

# Загрузка данных клиентов
def load_customers():
    try:
        if not os.path.exists(CUSTOMERS_FILE):
            logger.warning(f"Файл не существует: {CUSTOMERS_FILE}")
            return {}
        with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
            logger.info(f"Загрузка данных из файла: {CUSTOMERS_FILE}")
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Файл не найден: {CUSTOMERS_FILE}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле: {CUSTOMERS_FILE}")
        return {}

# Сохранение данных клиентов
def save_customers(customers):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, indent=2, ensure_ascii=False)
        logger.info(f"Данные сохранены в файл: {CUSTOMERS_FILE}")

# Загрузка транзакций
def load_transactions():
    try:
        if not os.path.exists(TRANSACTIONS_FILE):
            logger.warning(f"Файл транзакций не существует: {TRANSACTIONS_FILE}")
            return []
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
            logger.info(f"Загрузка данных из файла: {TRANSACTIONS_FILE}")
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Файл транзакций не найден: {TRANSACTIONS_FILE}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле: {TRANSACTIONS_FILE}")
        return []

# Добавление нового клиента
def add_customer(phone, name, birth_date, role="client"):
    """
    Добавляет нового клиента с ролью.
    :param phone: Номер телефона клиента
    :param name: ФИО клиента
    :param birth_date: Дата рождения клиента
    :param role: Роль клиента ('client' или 'user')
    :return: Сообщение об успешном добавлении
    """
    customers = load_customers()
    if phone in customers:
        raise ValueError("Клиент уже существует.")
    customers[phone] = {
        "name": name,
        "birth_date": birth_date,
        "balance": 0,
        "role": role  # Добавляем роль
    }
    save_customers(customers)
    return {"message": "Клиент добавлен."}

# Получение информации о клиенте
def get_customer(phone: str):
    customers = load_customers()
    if phone not in customers:
        raise HTTPException(status_code=404, detail="Клиент не найден.")
    transactions = load_transactions_for_customer(phone)
    return {
        "customer": customers[phone],
        "transactions": transactions
    }

# Обновление баланса клиента
def update_balance(phone: str, amount: float, transaction_type: str, operator: str):
    """
    Обновляет баланс клиента.
    :param phone: Номер телефона клиента
    :param amount: Сумма операции
    :param transaction_type: Тип операции ("add" или "deduct")
    :param operator: Имя оператора
    :return: Словарь с сообщением и новым балансом
    """
    customers = load_data("customers.json")

    if phone not in customers:
        raise ValueError("Клиент не найден.")

    customer = customers[phone]

    if transaction_type == "add":
        customer["balance"] += amount
    elif transaction_type == "deduct":
        if customer["balance"] < amount:
            raise ValueError("Недостаточно средств на балансе.")
        customer["balance"] -= amount

    save_data("customers.json", customers)

    return {"message": "Операция выполнена.", "balance": customer["balance"]}


# Добавление транзакции
def add_transaction(phone, transaction_type, amount):
    transactions = load_transactions()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transactions.append({
        "phone": phone,
        "type": transaction_type,
        "amount": amount,
        "timestamp": timestamp
    })
    # save_transactions(transactions)

# Получение списка клиентов
def list_customers():
    customers = load_customers()
    return {"customers": [
        f"Телефон: {phone}, ФИО: {data['name']}, Роль: {data['role']}"  # Добавляем роль
        for phone, data in customers.items()
    ]}

# Загрузка транзакций для конкретного клиента
def load_transactions_for_customer(phone):
    transactions = load_transactions()
    return [t for t in transactions if t["phone"] == phone]

def calculate_balance(phone: str) -> float:
    """
    Рассчитывает баланс клиента на основе транзакций.
    :param phone: Номер телефона клиента
    :return: Текущий баланс клиента
    """
    transactions = load_data(TRANSACTIONS_FILE)
    balance = sum(t["amount"] for t in transactions if t["phone"] == phone)
    return balance

def get_customer_info(phone: str) -> dict:
    """
    Возвращает информацию о клиенте (имя и баланс).
    :param phone: Номер телефона клиента
    :return: Словарь с информацией о клиенте
    """
    customers = load_data("customers.json")
    customer = next((c for c in customers if c["phone"] == phone), None)
    if not customer:
        raise ValueError("Клиент не найден.")

    # Рассчитываем баланс из транзакций
    balance = calculate_balance(phone)

    # Обновляем баланс в файле customers.json
    customer["balance"] = balance
    save_data("customers.json", customers)

    return {
        "name": customer["name"],
        "balance": balance
    }