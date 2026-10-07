import json
import logging
import os
import random
from typing import Any

from config import NS1, NS2, NS3, NS4

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_FILE = os.path.join(BASE_DIR, "pending.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
NEWSLETTER_MESSAGES = [NS1, NS2, NS3, NS4]

def create_json_file(file_path: str, default_data: Any = None) -> None:
    if os.path.exists(file_path): return
    if default_data is None: default_data = []
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(default_data, file, indent=4, ensure_ascii=False)

def load_json(file_path: str, default_data: Any = None) -> Any:
    if default_data is None: default_data = []
    create_json_file(file_path, default_data)
    try:
        with open(file_path, "r", encoding="utf-8") as file: return json.load(file)
    except (json.JSONDecodeError, OSError):
        logger.exception("Failed to read JSON file: %s", file_path)
        return default_data

def save_json(file_path: str, data: Any) -> bool:
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except OSError:
        logger.exception("Failed to save JSON file: %s", file_path)
        return False

def get_pending_users() -> list[int]:
    data = load_json(PENDING_FILE, [])
    if not isinstance(data, list): return []
    users = []
    for user_id in data:
        try: users.append(int(user_id))
        except (TypeError, ValueError): pass
    return users

def is_user_pending(user_id: int) -> bool: return int(user_id) in get_pending_users()

def add_pending_user(user_id: int) -> bool:
    user_id = int(user_id); users = get_pending_users()
    if user_id in users: return False
    users.append(user_id); return save_json(PENDING_FILE, users)

def remove_pending_user(user_id: int) -> bool:
    user_id = int(user_id); users = get_pending_users()
    if user_id not in users: return False
    users.remove(user_id); return save_json(PENDING_FILE, users)

def get_users() -> list[int]:
    data = load_json(USERS_FILE, [])
    if not isinstance(data, list): return []
    users = []
    for user_id in data:
        try: users.append(int(user_id))
        except (TypeError, ValueError): pass
    return users

def add_user(user_id: int) -> bool:
    user_id = int(user_id); users = get_users()
    if user_id in users: return False
    users.append(user_id); return save_json(USERS_FILE, users)

def remove_user(user_id: int) -> bool:
    user_id = int(user_id); users = get_users()
    if user_id not in users: return False
    users.remove(user_id); return save_json(USERS_FILE, users)

def pending_user_count() -> int: return len(get_pending_users())

async def send_random_newsletter(user_id: int, userbots: list) -> bool:
    if not userbots: return False
    try:
        await random.choice(userbots).send_message(int(user_id), random.choice(NEWSLETTER_MESSAGES))
        return True
    except Exception:
        logger.exception("Failed to send newsletter to user_id=%s", user_id)
        return False

def setup(bot):
    create_json_file(PENDING_FILE, [])
    create_json_file(USERS_FILE, [])
    logger.info("Function utilities initialized.")
