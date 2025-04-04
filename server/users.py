import json
import os
import logging
import bcrypt

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение абсолютного пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


# Загрузка данных пользователей
def load_users():
    try:
        if not os.path.exists(USERS_FILE):
            logger.warning(f"Файл не существует: {USERS_FILE}")
            return {}
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            logger.info(f"Загрузка данных из файла: {USERS_FILE}")
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Файл не найден: {USERS_FILE}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле: {USERS_FILE}")
        return {}


# Сохранение данных пользователей
def save_users(users):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
        logger.info(f"Данные сохранены в файл: {USERS_FILE}")


# Добавление нового пользователя
def add_user(username, password, role="seller"):
    """
    Добавляет нового пользователя с хешированным паролем.
    :param username: Имя пользователя
    :param password: Пароль пользователя (в открытом виде)
    :param role: Роль пользователя ('admin' или 'seller')
    :return: Сообщение об успешном добавлении
    """
    users = load_users()
    if username in users:
        raise ValueError("Пользователь уже существует.")

    # Хешируем пароль
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users[username] = {
        "password": hashed_password.decode("utf-8"),  # Сохраняем хеш как строку
        "role": role
    }
    save_users(users)
    return {"message": "Пользователь добавлен."}


# Аутентификация пользователя
def authenticate_user(username, password):
    """
    Проверяет логин и пароль пользователя.
    :param username: Имя пользователя
    :param password: Пароль пользователя (в открытом виде)
    :return: Роль пользователя, если аутентификация успешна
    """
    users = load_users()
    if username not in users:
        raise ValueError("Неверное имя пользователя или пароль.")

    # Получаем хеш пароля из базы
    stored_password_hash = users[username]["password"].encode("utf-8")

    # Проверяем совпадение паролей
    if not bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
        raise ValueError("Неверное имя пользователя или пароль.")

    return users[username]["role"]