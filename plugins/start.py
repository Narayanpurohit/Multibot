import logging

from telethon import events

logger = logging.getLogger(__name__)


def setup(bot):
    """Register the /start command handler."""

    @bot.on(events.NewMessage(pattern=r"^/start(?:\s+.*)?$"))
    async def start_command(event):
        try:
            sender = await event.get_sender()
            name = getattr(sender, "first_name", None) or "there"
            user_id = getattr(sender, "id", "unknown")

            logger.info("/start received from user_id=%s", user_id)

            await event.respond(
                f"Hello {name}! 👋\n"
                "Bot is online and ready."
            )

        except Exception:
            logger.exception("Error handling /start command.")