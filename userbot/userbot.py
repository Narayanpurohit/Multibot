import asyncio
import logging
import random

from telethon import TelegramClient, events

from config import A_CHAT_ID

from plugins.function import (
    add_pending_user,
    is_user_pending,
    send_random_newsletter,
    add_user,
    remove_user,
)


logger = logging.getLogger(__name__)

# Protect the pending check + add operation from duplicate processing
# when multiple messages from the same/new users arrive together.
pending_lock = asyncio.Lock()


def setup(
    userbot: TelegramClient,
    userbots: list[TelegramClient] | None = None,
):
    """
    Register the incoming group-message handler.

    Flow:
    1. Ignore Telegram bot accounts.
    2. Resolve the user's peer.
    3. Wait a random 5-50 seconds.
    4. Check pending.json.
    5. If the user is new, save the ID to pending.json.
    6. Run the initial newsletter/permission-message function.
    """
    if userbots is None:
        userbots = [userbot]


    @userbot.on(events.NewMessage(incoming=True, pattern=r"^/(subscribe|stop)(?:@\\w+)?$"))
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
                    if added else
                    "ℹ️ You are already subscribed."
                )
            else:
                removed = remove_user(user_id)
                await event.respond(
                    "🛑 You have been unsubscribed."
                    if removed else
                    "ℹ️ You are not subscribed."
                )
        except Exception:
            logger.exception("Error handling subscription command.")

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

            # Ignore Telegram bot accounts.
            if getattr(sender, "bot", False):
                logger.info(
                    "Ignoring bot sender: user_id=%s",
                    getattr(sender, "id", "unknown"),
                )
                return

            user_id = int(sender.id)

            # Resolve the user's peer before applying the delay.
            try:
                peer = await userbot.get_input_entity(user_id)
            except Exception:
                logger.exception(
                    "Failed to resolve peer for user_id=%s",
                    user_id,
                )
                return

            logger.info(
                "Peer resolved for user_id=%s: %s",
                user_id,
                type(peer).__name__,
            )

            # Random delay between 5 and 50 seconds.
            delay = random.uniform(5, 50)

            logger.info(
                "Waiting %.2f seconds before pending check for user_id=%s",
                delay,
                user_id,
            )

            await asyncio.sleep(delay)

            # Only the pending check + add operation is locked.
            # The network send happens outside the lock.
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

            # Run the initial newsletter/permission-message function.
            await send_random_newsletter(user_id, userbots)

        except Exception:
            logger.exception("Error handling incoming group message.")


def setup_all(userbots: list[TelegramClient]):
    """Register the handler on every configured userbot account."""
    if not userbots:
        logger.warning("No userbot accounts are configured.")
        return

    if not A_CHAT_ID:
        logger.warning("A_CHAT_ID is empty. No group messages will be processed.")

    for userbot in userbots:
        setup(userbot, userbots)
        logger.info("Userbot group-message handler loaded.")
