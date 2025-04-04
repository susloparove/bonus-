import json
import os
from datetime import datetime
from fastapi import HTTPException
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение абсолютного пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")

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
def update_balance(phone, amount, transaction_type):
    customers = load_customers()
    if phone not in customers:
        raise HTTPException(status_code=404, detail="Клиент не найден.")
    if transaction_type == "deduct" and customers[phone]["balance"] < abs(amount):
        raise ValueError("Недостаточно средств.")
    customers[phone]["balance"] += amount
    save_customers(customers)
    add_transaction(phone, transaction_type, amount)
    return {"message": f"Баланс обновлен.", "balance": customers[phone]["balance"]}

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
    save_transactions(transactions)

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