import json
import os
from datetime import datetime
from fastapi import HTTPException
import logging
from .utils import load_data, save_data

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")


def load_customers() -> dict:
    if not os.path.exists(CUSTOMERS_FILE):
        logger.warning(f"Файл не существует: {CUSTOMERS_FILE}")
        return {}
    try:
        with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки customers.json: {e}")
        return {}


def save_customers(customers: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, indent=2, ensure_ascii=False)


def add_customer(phone: str, name: str, birth_date: str, role="client"):
    customers = load_customers()
    if phone in customers:
        raise ValueError("Клиент уже существует.")
    customers[phone] = {
        "name": name,
        "birth_date": birth_date,
        "balance": 0.0,
        "role": role
    }
    save_customers(customers)
    return {"message": "Клиент добавлен."}


def update_balance(phone: str, amount: float, transaction_type: str, operator: str):
    customers = load_customers()
    if phone not in customers:
        raise ValueError("Клиент не найден.")

    customer = customers[phone]
    if transaction_type == "add":
        customer["balance"] += amount
    elif transaction_type == "deduct":
        if customer["balance"] < amount:
            raise ValueError("Недостаточно средств.")
        customer["balance"] -= amount
    else:
        raise ValueError("Неверный тип транзакции.")

    save_customers(customers)
    return {"message": "Операция выполнена.", "balance": customer["balance"]}


def list_customers():
    customers = load_customers()
    result = []
    for phone, data in customers.items():
        balance = data.get("balance", 0)
        result.append(f"{phone} |{data['name']} |Баланс: {balance}₿")
    return {"customers": result}



def get_customer(phone: str):
    customers = load_customers()
    if phone not in customers:
        raise HTTPException(status_code=404, detail="Клиент не найден.")

    transactions = load_transactions_for_customer(phone)

    return {
        "customer": customers[phone],
        "transactions": transactions
    }


def load_transactions() -> list:
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    try:
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки transactions.json: {e}")
        return []


def save_transactions(transactions: list):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)


def load_transactions_for_customer(phone: str) -> list:
    return [t for t in load_transactions() if t["phone"] == phone]


def calculate_balance(phone: str) -> float:
    return sum(t["amount"] for t in load_transactions() if t["phone"] == phone)


def get_customer_info(phone: str) -> dict:
    customers = load_customers()
    if phone not in customers:
        raise ValueError("Клиент не найден.")

    customer = customers[phone]
    balance = calculate_balance(phone)
    customer["balance"] = balance
    save_customers(customers)

    return {
        "name": customer["name"],
        "balance": round(balance, 2)
    }
