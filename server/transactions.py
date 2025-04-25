# server/transactions.py

import json
import os
from datetime import datetime
import logging
from server.utils import update_balance
from server.logger import log_action

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")

# Убедимся, что директория существует
os.makedirs(DATA_DIR, exist_ok=True)

def load_transactions():
    """
    Загружает все транзакции из файла
    """
    try:
        if not os.path.exists(TRANSACTIONS_FILE):
            return []
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка при загрузке транзакций: {e}")
        return []

def save_transactions(transactions):
    """
    Сохраняет список транзакций в файл
    """
    try:
        with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка при сохранении транзакций: {e}")

def add_transaction(phone: str, transaction_type: str, amount: float, operator: str):
    """
    Добавляет одну транзакцию в список и сохраняет
    """
    transactions = load_transactions()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    signed_amount = amount if transaction_type == "add" else -abs(amount)

    transaction = {
        "phone": phone,
        "type": transaction_type,
        "amount": signed_amount,
        "timestamp": timestamp,
        "operator": operator
    }

    transactions.append(transaction)
    save_transactions(transactions)

def add_bonus(phone: str, amount: float, operator: str):
    """
    Пополнение бонусного счёта
    """
    response = update_balance(phone, amount, "add", operator)
    add_transaction(phone, "add", amount, operator)
    log_action(operator, "Пополнение", phone, amount)
    return response

def deduct_bonus(phone: str, amount: float, operator: str):
    """
    Списание с бонусного счёта
    """
    response = update_balance(phone, amount, "deduct", operator)
    add_transaction(phone, "deduct", amount, operator)
    log_action(operator, "Списание", phone, amount)
    return response
