# server/log_viewer.py

import os
import json
from fastapi import HTTPException

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "logs", "actions.json")

def get_action_log(limit: int = 10, offset: int = 0) -> list:
    """
    Возвращает последние действия из журнала логов.
    :param limit: Сколько последних записей вернуть (по умолчанию 10)
    :return: Список записей лога
    """
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
            return logs[-(offset + limit):-offset or None]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения лога: {e}")
