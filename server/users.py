# server/users.py

import json
import os
from datetime import datetime
import bcrypt  # Не забудьте установить библиотеку: pip install bcrypt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def load_users():
    """
    Загружает данные пользователей из файла users.json.
    :return: Словарь с данными пользователей
    """
    try:
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users_data):
    """
    Сохраняет данные пользователей в файл users.json.
    :param users_data: Словарь с данными пользователей
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)

def authenticate_user(username: str, password: str) -> bool:
    """
    Аутентифицирует пользователя по имени и паролю.
    :param username: Имя пользователя
    :param password: Пароль
    :return: True, если аутентификация успешна, иначе False
    """
    users = load_users()
    user_data = users.get(username)
    if not user_data:
        return False
    stored_password_hash = user_data["password"].encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), stored_password_hash)

def get_user_role(username: str) -> str:
    """
    Возвращает роль пользователя по его имени.
    :param username: Имя пользователя
    :return: Роль пользователя ("admin", "seller" или "unknown")
    """
    users = load_users()
    user_data = users.get(username)
    if not user_data:
        return "unknown"
    return user_data.get("role", "unknown")

def add_user(username: str, password: str, role: str):
    """
    Добавляет нового пользователя.
    :param username: Имя пользователя
    :param password: Пароль
    :param role: Роль пользователя ("admin" или "seller")
    """
    users = load_users()
    if username in users:
        raise ValueError("Пользователь с таким именем уже существует.")
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users[username] = {
        "password": password_hash.decode("utf-8"),
        "role": role,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_users(users)

def authenticate_user_by_password(password: str) -> str:
    """
    Аутентифицирует пользователя по паролю.
    :param password: Пароль
    :return: Имя пользователя, если аутентификация успешна
    """
    users = load_users()
    for username, user_data in users.items():
        stored_password_hash = user_data["password"].encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
            return username
    raise ValueError("Неверное имя пользователя или пароль.")