import json
import logging
import os
import random
from typing import Any

from config import NS1, NS2, NS3, NS4, OWNER_ID

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_FILE = os.path.join(BASE_DIR, "pending.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
USERBOT_USERS_FILE = os.path.join(BASE_DIR, "userbot_users.json")
NEWSLETTER_MESSAGES = [NS1, NS2, NS3, NS4]


def create_json_file(file_path: str, default_data: Any = None) -> None:
    if os.path.exists(file_path):
        return
    if default_data is None:
        default_data = []
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(default_data, file, indent=4, ensure_ascii=False)


def load_json(file_path: str, default_data: Any = None) -> Any:
    if default_data is None:
        default_data = []
    create_json_file(file_path, default_data)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
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
    if not isinstance(data, list):
        return []
    users = []
    for user_id in data:
        try:
            users.append(int(user_id))
        except (TypeError, ValueError):
            pass
    return users


def is_user_pending(user_id: int) -> bool:
    return int(user_id) in get_pending_users()


def add_pending_user(user_id: int) -> bool:
    user_id = int(user_id)
    users = get_pending_users()
    if user_id in users:
        return False
    users.append(user_id)
    return save_json(PENDING_FILE, users)


def remove_pending_user(user_id: int) -> bool:
    user_id = int(user_id)
    users = get_pending_users()
    if user_id not in users:
        return False
    users.remove(user_id)
    return save_json(PENDING_FILE, users)


def get_users() -> list[int]:
    data = load_json(USERS_FILE, [])
    if not isinstance(data, list):
        return []
    users = []
    for user_id in data:
        try:
            users.append(int(user_id))
        except (TypeError, ValueError):
            pass
    return users


def add_user(user_id: int) -> bool:
    user_id = int(user_id)
    users = get_users()
    if user_id in users:
        return False
    users.append(user_id)
    return save_json(USERS_FILE, users)


def remove_user(user_id: int) -> bool:
    user_id = int(user_id)
    users = get_users()
    if user_id not in users:
        return False
    users.remove(user_id)
    return save_json(USERS_FILE, users)


def get_userbot_indexes(user_id: int) -> list[int]:
    data = load_json(USERBOT_USERS_FILE, {"users": {}})
    users = data.get("users", {}) if isinstance(data, dict) else {}
    indexes = users.get(str(int(user_id)), [])
    if not isinstance(indexes, list):
        return []

    result = []
    for index in indexes:
        try:
            index = int(index)
            if index > 0 and index not in result:
                result.append(index)
        except (TypeError, ValueError):
            pass
    return result


def mark_userbot_for_user(user_id: int, userbot_index: int) -> bool:
    data = load_json(USERBOT_USERS_FILE, {"users": {}})
    if not isinstance(data, dict):
        data = {"users": {}}
    users = data.setdefault("users", {})
    key = str(int(user_id))
    indexes = users.setdefault(key, [])

    if not isinstance(indexes, list):
        indexes = []
        users[key] = indexes

    userbot_index = int(userbot_index)
    if userbot_index in indexes:
        return False

    indexes.append(userbot_index)
    return save_json(USERBOT_USERS_FILE, data)


def pending_user_count() -> int:
    return len(get_pending_users())


async def notify_owner(
    message: str,
    userbots: list,
) -> bool:
    if not OWNER_ID or not userbots:
        return False

    for userbot in userbots:
        try:
            await userbot.send_message(int(OWNER_ID), message)
            return True
        except Exception:
            logger.exception("Failed to notify owner.")
    return False


async def send_random_newsletter(
    user_id: int,
    marked_userbots: list,
    all_userbots: list | None = None,
) -> bool:
    if not marked_userbots:
        await notify_owner(
            f"❌ Newsletter error\\nUser ID: {user_id}\\n"
            "No userbot is marked for this user.",
            all_userbots or [],
        )
        return False

    try:
        userbot = random.choice(marked_userbots)
        await userbot.send_message(
            int(user_id),
            random.choice(NEWSLETTER_MESSAGES),
        )
        return True
    except Exception as error:
        logger.exception("Failed to send newsletter to user_id=%s", user_id)
        await notify_owner(
            f"❌ Newsletter error\\n"
            f"User ID: {user_id}\\n"
            f"Error: {type(error).__name__}: {error}",
            all_userbots or marked_userbots,
        )
        return False


def setup(bot):
    create_json_file(PENDING_FILE, [])
    create_json_file(USERS_FILE, [])
    create_json_file(USERBOT_USERS_FILE, {"users": {}})
    logger.info("Function utilities initialized.")
