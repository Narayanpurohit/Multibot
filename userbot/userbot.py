import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from plugins.function import add_pending_user, is_user_pending, send_random_newsletter


logger = logging.getLogger(__name__)


def setup(userbot: Client, userbots: list[Client] | None = None):
    """
    Register the A_Chat message handler on a userbot.

    New human users are added to pending.json before the initial
    newsletter/permission message is sent.
    """
    if userbots is None:
        userbots = [userbot]

    @userbot.on_message(filters.private)
    async def incoming_private_message(client: Client, message: Message):
        try:
            user = message.from_user

            # Ignore messages without a normal user sender.
            if not user:
                return

            # Ignore Telegram bot accounts.
            if user.is_bot:
                logger.info("Ignoring bot sender: user_id=%s", user.id)
                return

            user_id = int(user.id)

            # Ignore users that have already been processed.
            if is_user_pending(user_id):
                return

            # Mark the user as processed before sending the initial message.
            if not add_pending_user(user_id):
                return

            logger.info(
                "New human user detected: user_id=%s",
                user_id,
            )

            # Send the configured permission/newsletter message.
            await send_random_newsletter(user_id, userbots)

        except Exception:
            logger.exception("Error handling incoming userbot message.")


def setup_all(userbots: list[Client]):
    """Register the handler on every configured userbot account."""
    for userbot in userbots:
        setup(userbot, userbots)
        logger.info("Userbot message handler loaded.")
