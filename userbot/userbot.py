import logging
import random

from pyrogram import Client, filters
from pyrogram.types import Message

from plugins.function import add_pending_user, is_user_pending, send_random_newsletter


logger = logging.getLogger(__name__)


def setup(userbot: Client, userbots: list[Client] | None = None):
    """
    Register the A_Chat message handler on a userbot.

    Flow:
    1. Ignore bot accounts.
    2. Resolve the user's peer.
    3. Wait a random 5-50 seconds.
    4. Check pending.json.
    5. If the user is new, save the ID to pending.json.
    6. Run the newsletter/permission-message function.
    """
    if userbots is None:
        userbots = [userbot]

    @userbot.on_message(filters.private)
    async def incoming_private_message(client: Client, message: Message):
        try:
            user = message.from_user

            if not user:
                return

            # Ignore Telegram bot accounts.
            if user.is_bot:
                logger.info("Ignoring bot sender: user_id=%s", user.id)
                return

            user_id = int(user.id)

            # Resolve the user's peer before applying the delay.
            try:
                peer = await client.resolve_peer(user_id)
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
            await __import__("asyncio").sleep(delay)

            # Check pending.json only after the delay.
            if is_user_pending(user_id):
                logger.info(
                    "User already pending after delay: user_id=%s",
                    user_id,
                )
                return

            # Save only new users.
            if not add_pending_user(user_id):
                return

            logger.info(
                "New human user saved to pending.json: user_id=%s",
                user_id,
            )

            # Run the initial newsletter/permission-message function.
            await send_random_newsletter(user_id, userbots)

        except Exception:
            logger.exception("Error handling incoming userbot message.")


def setup_all(userbots: list[Client]):
    """Register the handler on every configured userbot account."""
    for userbot in userbots:
        setup(userbot, userbots)
        logger.info("Userbot message handler loaded.")
