import json
import logging
import os
import random
from typing import Any

from config import NS1, NS2, NS3, NS4


logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_FILE = os.path.join(BASE_DIR, "pending.json")

NEWSLETTER_MESSAGES = [NS1, NS2, NS3, NS4]


def create_json_file(file_path: str, default_data: Any = None) -> None:
    """Create a JSON file if it does not already exist."""
    if os.path.exists(file_path):
        return

    if default_data is None:
        default_data = []

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(default_data, file, indent=4, ensure_ascii=False)

    logger.info("Created JSON file: %s", file_path)


def load_json(file_path: str, default_data: Any = None) -> Any:
    """Load JSON data. Creates the file when it does not exist."""
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
    """Save data to a JSON file."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except OSError:
        logger.exception("Failed to save JSON file: %s", file_path)
        return False


def get_pending_users() -> list[int]:
    """Return user IDs stored in pending.json."""
    data = load_json(PENDING_FILE, [])

    if not isinstance(data, list):
        logger.warning("pending.json does not contain a list.")
        return []

    users = []

    for user_id in data:
        try:
            users.append(int(user_id))
        except (TypeError, ValueError):
            logger.warning("Ignoring invalid user ID in pending.json: %r", user_id)

    return users


def is_user_pending(user_id: int) -> bool:
    """Check whether a user ID already exists in pending.json."""
    return int(user_id) in get_pending_users()


def add_pending_user(user_id: int) -> bool:
    """Add a user ID to pending.json if it is not already present."""
    user_id = int(user_id)
    users = get_pending_users()

    if user_id in users:
        return False

    users.append(user_id)
    return save_json(PENDING_FILE, users)


def remove_pending_user(user_id: int) -> bool:
    """Remove a user ID from pending.json if present."""
    user_id = int(user_id)
    users = get_pending_users()

    if user_id not in users:
        return False

    users.remove(user_id)
    return save_json(PENDING_FILE, users)


def pending_user_count() -> int:
    """Return the number of pending users."""
    return len(get_pending_users())


async def send_random_newsletter(user_id: int, userbots: list) -> bool:
    """Send a random configured newsletter message using a random userbot.

    Use this only for users who have explicitly opted in to the newsletter.
    This function does not retry or rotate accounts to bypass Telegram limits.
    """
    if not userbots:
        logger.warning("No userbots are available for newsletter delivery.")
        return False

    userbot = random.choice(userbots)
    message = random.choice(NEWSLETTER_MESSAGES)

    try:
        await userbot.send_message(
            chat_id=int(user_id),
            text=message,
        )

        logger.info(
            "Newsletter sent to user_id=%s using selected userbot.",
            user_id,
        )
        return True

    except Exception:
        logger.exception(
            "Failed to send newsletter to user_id=%s.",
            user_id,
        )
        return False


def setup(bot):
    """Plugin entry point. Utility functions are imported where needed."""
    create_json_file(PENDING_FILE, [])
    logger.info("Function utilities initialized.")
