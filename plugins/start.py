import logging

from pyrogram import filters
from pyrogram.types import Message


logger = logging.getLogger(__name__)


def setup(bot):
    @bot.on_message(filters.command("start"))
    async def start_command(client, message: Message):
        try:
            user = message.from_user
            name = user.first_name if user else "there"

            logger.info(
                "/start received from user_id=%s",
                user.id if user else "unknown",
            )

            await message.reply_text(
                f"Hello {name}! 👋\n"
                "Bot is online and ready."
            )

        except Exception:
            logger.exception("Error handling /start command.")
            raise
