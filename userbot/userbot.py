import asyncio
import logging
import random

from telethon import TelegramClient, events

from config import A_CHAT_ID

from plugins.function import (
    add_pending_user,
    get_userbot_indexes,
    is_user_pending,
    mark_userbot_for_user,
    notify_owner,
    remove_pending_user,
    send_random_newsletter,
    add_user,
    remove_user,
)


logger = logging.getLogger(__name__)

# Protect the pending check + add operation from duplicate processing.
pending_lock = asyncio.Lock()


def setup(
    userbot: TelegramClient,
    userbots: list[TelegramClient] | None = None,
    userbot_index: int = 1,
):
    """Register handlers for one userbot account."""
    if userbots is None:
        userbots = [userbot]

    @userbot.on(events.NewMessage(
        incoming=True,
        pattern=r"^/(subscribe|stop)(?:@\w+)?$",
    ))
    async def subscription_command(event):
        try:
            if not event.is_private:
                return

            sender = await event.get_sender()
            if not sender or getattr(sender, "bot", False):
                return

            user_id = int(sender.id)
            command = event.pattern_match.group(1).lower()

            if command == "subscribe":
                added = add_user(user_id)
                await event.respond(
                    "✅ You are subscribed to the newsletter."
                    if added
                    else
                    "ℹ️ You are already subscribed."
                )
            else:
                removed = remove_user(user_id)
                await event.respond(
                    "🛑 You have been unsubscribed."
                    if removed
                    else
                    "ℹ️ You are not subscribed."
                )
        except Exception as error:
            logger.exception("Error handling subscription command.")
            await notify_owner(
                f"❌ Subscription handler error\\n"
                f"Error: {type(error).__name__}: {error}",
                userbots,
            )

    @userbot.on(events.NewMessage(incoming=True))
    async def incoming_group_message(event):
        try:
            if not event.is_group:
                return

            if event.chat_id not in A_CHAT_ID:
                return

            sender = await event.get_sender()

            if not sender:
                return

            if getattr(sender, "bot", False):
                logger.info(
                    "Ignoring bot sender: user_id=%s",
                    getattr(sender, "id", "unknown"),
                )
                return

            user_id = int(sender.id)

            # Keep the input entity from the account that actually
            # received the group message.
            try:
                await event.get_input_sender()
            except Exception as error:
                logger.exception(
                    "Failed to resolve input sender for user_id=%s",
                    user_id,
                )
                await notify_owner(
                    f"❌ Peer/entity error\\n"
                    f"User ID: {user_id}\\n"
                    f"Userbot: {userbot_index}\\n"
                    f"Error: {type(error).__name__}: {error}",
                    userbots,
                )
                return

            # Mark this account as an account that has encountered the user.
            mark_userbot_for_user(user_id, userbot_index)

            logger.info(
                "Marked userbot %d for user_id=%s",
                userbot_index,
                user_id,
            )

            delay = random.uniform(5, 50)

            logger.info(
                "Waiting %.2f seconds before pending check for user_id=%s",
                delay,
                user_id,
            )

            await asyncio.sleep(delay)

            async with pending_lock:
                if is_user_pending(user_id):
                    logger.info(
                        "User already pending after delay: user_id=%s",
                        user_id,
                    )
                    return

                if not add_pending_user(user_id):
                    logger.info(
                        "User was already added to pending.json: user_id=%s",
                        user_id,
                    )
                    return

            logger.info(
                "New human user saved to pending.json: user_id=%s",
                user_id,
            )

            marked_indexes = get_userbot_indexes(user_id)
            marked_userbots = [
                userbots[index - 1]
                for index in marked_indexes
                if 1 <= index <= len(userbots)
            ]

            # Only accounts marked for this user are passed to the
            # newsletter function.
            sent = await send_random_newsletter(
                user_id,
                marked_userbots,
                userbots,
            )

            if not sent:
                # If the newsletter was not sent, allow a later group
                # message to retry instead of leaving the user stuck.
                remove_pending_user(user_id)

        except Exception as error:
            logger.exception("Error handling incoming group message.")
            await notify_owner(
                f"❌ Group handler error\\n"
                f"User ID: {locals().get('user_id', 'unknown')}\\n"
                f"Userbot: {userbot_index}\\n"
                f"Error: {type(error).__name__}: {error}",
                userbots,
            )


def setup_all(userbots: list[TelegramClient]):
    """Register handlers on every configured userbot account."""
    if not userbots:
        logger.warning("No userbot accounts are configured.")
        return

    if not A_CHAT_ID:
        logger.warning(
            "A_CHAT_ID is empty. No group messages will be processed."
        )

    for index, userbot in enumerate(userbots, start=1):
        setup(
            userbot,
            userbots,
            userbot_index=index,
        )
        logger.info(
            "Userbot group-message handler loaded for account %d.",
            index,
        )
