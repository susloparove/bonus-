# server/utils.py

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_data(file_name: str) -> list:
    """
    Загружает данные из JSON-файла.
    :param file_name: Имя файла (например, customers.json)
    :return: Список данных
    """
    file_path = os.path.join(DATA_DIR, file_name)
    try:
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(file_name: str, data: list):
    """
    Сохраняет данные в JSON-файл.
    :param file_name: Имя файла (например, customers.json)
    :param data: Данные для сохранения
    """
    file_path = os.path.join(DATA_DIR, file_name)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_balance(phone: str, amount: float, transaction_type: str, operator: str):
    """
    Обновляет баланс клиента.
    :param phone: Номер телефона клиента
    :param amount: Сумма операции
    :param transaction_type: Тип операции ("add" или "deduct")
    :param operator: Имя оператора
    :return: Сообщение об успешной операции
    """
    customers = load_data("customers.json")
    for customer in customers:
        if customer["phone"] == phone:
            if transaction_type == "add":
                customer["balance"] += amount
            elif transaction_type == "deduct":
                if customer["balance"] < amount:
                    raise ValueError("Недостаточно средств на балансе.")
                customer["balance"] -= amount
            save_data("customers.json", customers)
            return {"message": "Операция выполнена.", "balance": customer["balance"]}
    raise ValueError("Клиент не найден.")

def add_transaction(phone: str, transaction_type: str, amount: float, operator: str):
    """
    Добавляет транзакцию в файл transactions.json.
    :param phone: Номер телефона клиента
    :param transaction_type: Тип операции ("add" или "deduct")
    :param amount: Сумма операции
    :param operator: Имя оператора
    """
    transactions = load_data("transactions.json")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transactions.append({
        "phone": phone,
        "type": transaction_type,
        "amount": amount,
        "timestamp": timestamp,
        "operator": operator
    })
    save_data("transactions.json", transactions)