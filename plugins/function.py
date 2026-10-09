import asyncio
import json
import logging
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from telethon.tl.types import InputPeerUser

from config import NS1, NS2, NS3, NS4, OWNER_ID

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_FILE = os.path.join(BASE_DIR, "pending.json")
PENDING2_FILE = os.path.join(BASE_DIR, "pending2.json")
PENDING3_FILE = os.path.join(BASE_DIR, "pending3.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
USERBOT_USERS_FILE = os.path.join(BASE_DIR, "userbot_users.json")
USERBOT_STATE_FILE = os.path.join(BASE_DIR, "userbot.json")
NEWSLETTER_MESSAGES = [message for message in (NS1, NS2, NS3, NS4) if message]
COOLDOWN = timedelta(minutes=45)

_state_lock = asyncio.Lock()
_send_lock = asyncio.Lock()


def create_json_file(file_path: str, default_data: Any = None) -> None:
    if not os.path.exists(file_path):
        save_json(file_path, [] if default_data is None else default_data)


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
    temporary_path = file_path + ".tmp"
    try:
        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        os.replace(temporary_path, file_path)
        return True
    except OSError:
        logger.exception("Failed to save JSON file: %s", file_path)
        try:
            if os.path.exists(temporary_path):
                os.remove(temporary_path)
        except OSError:
            logger.exception("Failed to remove temporary JSON file.")
        return False


def _get_id_list(file_path: str) -> list[int]:
    data = load_json(file_path, [])
    if not isinstance(data, list):
        return []
    result = []
    for value in data:
        try:
            user_id = int(value)
            if user_id not in result:
                result.append(user_id)
        except (TypeError, ValueError):
            continue
    return result


def _add_id(file_path: str, user_id: int) -> bool:
    users = _get_id_list(file_path)
    user_id = int(user_id)
    if user_id in users:
        return False
    users.append(user_id)
    return save_json(file_path, users)


def _remove_id(file_path: str, user_id: int) -> bool:
    users = _get_id_list(file_path)
    user_id = int(user_id)
    if user_id not in users:
        return False
    users.remove(user_id)
    return save_json(file_path, users)


def get_pending_users() -> list[int]:
    return _get_id_list(PENDING_FILE)


def is_user_pending(user_id: int) -> bool:
    return int(user_id) in get_pending_users()


def add_pending_user(user_id: int) -> bool:
    return _add_id(PENDING_FILE, user_id)


def remove_pending_user(user_id: int) -> bool:
    return _remove_id(PENDING_FILE, user_id)


def get_users() -> list[int]:
    return _get_id_list(USERS_FILE)


def add_user(user_id: int) -> bool:
    return _add_id(USERS_FILE, user_id)


def remove_user(user_id: int) -> bool:
    return _remove_id(USERS_FILE, user_id)


def _load_userbot_state() -> dict:
    data = load_json(USERBOT_STATE_FILE, {"userbots": {}})
    if not isinstance(data, dict):
        data = {"userbots": {}}
    if not isinstance(data.get("userbots"), dict):
        data["userbots"] = {}
    return data


def save_resolved_peer(user_id: int, userbot_index: int, input_peer: Any) -> bool:
    """Persist account-specific InputPeerUser data, including its access hash."""
    if not isinstance(input_peer, InputPeerUser):
        logger.warning(
            "Unsupported input peer type for user_id=%s: %s",
            user_id, type(input_peer).__name__,
        )
        return False

    data = _load_userbot_state()
    account = data["userbots"].setdefault(str(int(userbot_index)), {
        "last_message_at": None, "users": {},
    })
    if not isinstance(account, dict):
        account = {"last_message_at": None, "users": {}}
        data["userbots"][str(int(userbot_index))] = account
    users = account.setdefault("users", {})
    users[str(int(user_id))] = {
        "user_id": int(input_peer.user_id),
        "access_hash": int(input_peer.access_hash),
    }
    return save_json(USERBOT_STATE_FILE, data)


def get_saved_peer(user_id: int, userbot_index: int) -> InputPeerUser | None:
    data = _load_userbot_state()
    account = data["userbots"].get(str(int(userbot_index)), {})
    users = account.get("users", {}) if isinstance(account, dict) else {}
    peer = users.get(str(int(user_id)), {}) if isinstance(users, dict) else {}
    try:
        return InputPeerUser(
            user_id=int(peer["user_id"]),
            access_hash=int(peer["access_hash"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def mark_userbot_for_user(user_id: int, userbot_index: int) -> bool:
    """Keep the existing user-to-account index map for compatibility."""
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


def get_userbot_indexes(user_id: int) -> list[int]:
    data = load_json(USERBOT_USERS_FILE, {"users": {}})
    users = data.get("users", {}) if isinstance(data, dict) else {}
    indexes = users.get(str(int(user_id)), []) if isinstance(users, dict) else []
    if not isinstance(indexes, list):
        return []
    result = []
    for value in indexes:
        try:
            index = int(value)
            if index > 0 and index not in result:
                result.append(index)
        except (TypeError, ValueError):
            continue
    return result


def pending_user_count() -> int:
    return len(get_pending_users())


async def notify_owner(message: str, userbots: list) -> bool:
    if not OWNER_ID or not userbots:
        return False
    for userbot in userbots:
        try:
            await userbot.send_message(int(OWNER_ID), message)
            return True
        except Exception:
            logger.exception("Failed to notify owner.")
    return False


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _eligible_account_indexes(user_id: int, userbots: list) -> list[int]:
    data = _load_userbot_state()
    accounts = data["userbots"]
    now = datetime.now(timezone.utc)
    eligible = []
    for index, _client in enumerate(userbots, start=1):
        if get_saved_peer(user_id, index) is None:
            continue
        account = accounts.setdefault(str(index), {"last_message_at": None, "users": {}})
        last_sent = _parse_timestamp(account.get("last_message_at"))
        if last_sent is None or now - last_sent >= COOLDOWN:
            eligible.append(index)
    save_json(USERBOT_STATE_FILE, data)
    return eligible


def _seconds_until_next_account(user_id: int, userbots: list) -> float | None:
    data = _load_userbot_state()
    now = datetime.now(timezone.utc)
    remaining = []
    for index, _client in enumerate(userbots, start=1):
        if get_saved_peer(user_id, index) is None:
            continue
        account = data["userbots"].get(str(index), {})
        last_sent = _parse_timestamp(account.get("last_message_at"))
        if last_sent is None:
            return 0.0
        remaining.append(max(0.0, (last_sent + COOLDOWN - now).total_seconds()))
    return min(remaining) if remaining else None


async def _send_permission_message(user_id: int, userbots: list) -> bool:
    if not userbots:
        await notify_owner("❌ Permission-message error: no userbot accounts configured.", userbots)
        return False
    if not NEWSLETTER_MESSAGES:
        await notify_owner("❌ Permission-message error: NS1–NS4 are all empty.", userbots)
        return False

    # Serialize outgoing permission messages so two handlers cannot use
    # the same account concurrently or race the shared cooldown state.
    async with _send_lock:
        while True:
            eligible = _eligible_account_indexes(user_id, userbots)
            if eligible:
                index = random.choice(eligible)
                client = userbots[index - 1]
                peer = get_saved_peer(user_id, index)
                if peer is None:
                    continue
                try:
                    await client.send_message(peer, random.choice(NEWSLETTER_MESSAGES))
                    data = _load_userbot_state()
                    account = data["userbots"].setdefault(
                        str(index), {"last_message_at": None, "users": {}}
                    )
                    account["last_message_at"] = datetime.now(timezone.utc).isoformat()
                    if not save_json(USERBOT_STATE_FILE, data):
                        await notify_owner(
                            f"⚠️ Permission message sent to user_id={user_id}, "
                            "but userbot.json timestamp could not be saved.",
                            userbots,
                        )
                    logger.info(
                        "Permission message sent to user_id=%s by userbot=%d",
                        user_id, index,
                    )
                    return True
                except Exception as error:
                    logger.exception(
                        "Permission message failed for user_id=%s, userbot=%d",
                        user_id, index,
                    )
                    try:
                        from telethon.errors import FloodWaitError
                        if isinstance(error, FloodWaitError):
                            data = _load_userbot_state()
                            account = data["userbots"].setdefault(
                                str(index), {"last_message_at": None, "users": {}}
                            )
                            # Record the server-mandated wait as well as the normal cooldown.
                            account["last_message_at"] = (
                                datetime.now(timezone.utc)
                                + timedelta(seconds=max(error.seconds, int(COOLDOWN.total_seconds())))
                                - COOLDOWN
                            ).isoformat()
                            save_json(USERBOT_STATE_FILE, data)
                    except Exception:
                        logger.exception("Could not persist FloodWait state.")
                    await notify_owner(
                        f"❌ Permission-message error\nUser ID: {user_id}\n"
                        f"Userbot: {index}\nError: {type(error).__name__}: {error}",
                        userbots,
                    )
                    return False

            remaining = _seconds_until_next_account(user_id, userbots)
            if remaining is None:
                await notify_owner(
                    f"❌ Permission-message error\nUser ID: {user_id}\n"
                    "No configured userbot has saved peer information for this user.",
                    userbots,
                )
                return False
            # Jitter is added after the remaining cooldown; it never shortens it.
            await asyncio.sleep(max(0.0, remaining) + random.uniform(1, 3))


async def send_random_newsletter(
    user_id: int,
    marked_userbots: list,
    all_userbots: list | None = None,
) -> bool:
    """Compatibility wrapper; this function sends the permission prompt only."""
    return await process_permission_message(user_id, all_userbots or marked_userbots)


async def process_permission_message(user_id: int, userbots: list) -> bool:
    """Queue and send one permission prompt using pending2/pending3."""
    user_id = int(user_id)
    async with _state_lock:
        # A successful permission prompt is recorded in pending.json.
        # Do not send it again if a duplicate was queued during cooldown.
        if is_user_pending(user_id):
            return False
        pending2 = _get_id_list(PENDING2_FILE)
        if user_id in pending2:
            _add_id(PENDING3_FILE, user_id)
            logger.info("User %s already processing; queued duplicate in pending3.json", user_id)
            return True
        pending2.append(user_id)
        if not save_json(PENDING2_FILE, pending2):
            return False

    success = False
    try:
        success = await _send_permission_message(user_id, userbots)
        if success:
            # pending.json means the permission prompt was already sent/contacted.
            _add_id(PENDING_FILE, user_id)
    finally:
        async with _state_lock:
            _remove_id(PENDING2_FILE, user_id)
            pending3 = _get_id_list(PENDING3_FILE)
            next_user = pending3.pop(0) if pending3 else None
            save_json(PENDING3_FILE, pending3)
            active_users = _get_id_list(PENDING2_FILE)

        if next_user is not None and next_user not in active_users:
            await process_permission_message(next_user, userbots)

    return success


def setup(bot):
    create_json_file(PENDING_FILE, [])
    create_json_file(PENDING2_FILE, [])
    create_json_file(PENDING3_FILE, [])
    create_json_file(USERS_FILE, [])
    create_json_file(USERBOT_USERS_FILE, {"users": {}})
    create_json_file(USERBOT_STATE_FILE, {"userbots": {}})
    logger.info("Function utilities initialized.")
