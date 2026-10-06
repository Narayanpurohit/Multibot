import logging

from pyrogram import filters
from pyrogram.types import Message

from plugins.function import pending_user_count


logger = logging.getLogger(__name__)


def setup(bot):
    @bot.on_message(filters.command("stats"))
    async def stats_command(client, message: Message):
        try:
            count = pending_user_count()

            await message.reply_text(
                "📊 **Bot Stats**\n\n"
                f"👥 Pending Users: `{count}`"
            )

            logger.info(
                "/stats requested by user_id=%s | pending_users=%d",
                message.from_user.id if message.from_user else "unknown",
                count,
            )

        except Exception:
            logger.exception("Error handling /stats command.")
            raise