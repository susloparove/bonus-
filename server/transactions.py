import json
import os
from datetime import datetime
from server.customers import update_balance

# Определение абсолютного пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")

# Загрузка транзакций
def load_transactions():
    try:
        if not os.path.exists(TRANSACTIONS_FILE):
            return []
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

# Сохранение транзакций
def save_transactions(transactions):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

# Добавление транзакции
def add_transaction(phone, transaction_type, amount, operator):
    transactions = load_transactions()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transactions.append({
        "phone": phone,
        "type": transaction_type,
        "amount": amount,
        "timestamp": timestamp,
        "operator": operator
    })
    save_transactions(transactions)

# Пополнение баланса
def add_bonus(phone, amount, operator):
    """
    Пополняет баланс клиента.
    :param phone: Номер телефона клиента
    :param amount: Сумма пополнения
    :param operator: Имя оператора (пользователя, который провёл операцию)
    :return: Сообщение об успешном пополнении
    """
    response = update_balance(phone, amount, "add", operator)
    add_transaction(phone, "add", amount, operator)
    return response

# Списание баланса
def deduct_bonus(phone, amount, operator):
    """
    Списывает средства с баланса клиента.
    :param phone: Номер телефона клиента
    :param amount: Сумма списания
    :param operator: Имя оператора (пользователя, который провёл операцию)
    :return: Сообщение об успешном списании
    """
    response = update_balance(phone, amount, "deduct", operator)
    add_transaction(phone, "deduct", amount, operator)
    return response