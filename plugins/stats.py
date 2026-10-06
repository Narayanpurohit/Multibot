import logging

from telethon import events

from plugins.function import pending_user_count

logger = logging.getLogger(__name__)


def setup(bot):
    """Register the /stats command handler."""

    @bot.on(events.NewMessage(pattern=r"^/stats(?:\s+.*)?$"))
    async def stats_command(event):
        try:
            count = pending_user_count()
            sender = await event.get_sender()
            user_id = getattr(sender, "id", "unknown")

            await event.respond(
                "📊 **Bot Stats**\n\n"
                f"👥 Pending Users: `{count}`"
            )

            logger.info(
                "/stats requested by user_id=%s | pending_users=%d",
                user_id,
                count,
            )

        except Exception:
            logger.exception("Error handling /stats command.")