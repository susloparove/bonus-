import json
import os
from datetime import datetime
from server.utils import update_balance
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Определение корневой директории проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")

# Проверка существования папки data
os.makedirs(DATA_DIR, exist_ok=True)

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
    """
    Сохраняет данные транзакций в файл transactions.json.
    :param transactions: Список транзакций
    """
    # print(f"Корневая директория: {BASE_DIR}")
    # print(f"Путь к файлу транзакций: {TRANSACTIONS_FILE}")
    try:
        with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)
        # print(f"Транзакция сохранена в файл: {TRANSACTIONS_FILE}")  # Отладочный вывод
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
# Добавление транзакции
def add_transaction(phone: str, transaction_type: str, amount: float, operator: str):
    """
    Добавляет новую транзакцию.
    :param phone: Номер телефона клиента
    :param transaction_type: Тип операции ("add" или "deduct")
    :param amount: Сумма операции
    :param operator: Имя оператора
    """
    transactions = load_transactions()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Определяем знак суммы
    signed_amount = amount if transaction_type == "add" else -abs(amount)

    transactions.append({
        "phone": phone,
        "type": transaction_type,
        "amount": signed_amount,  # Сохраняем сумму с учётом знака
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