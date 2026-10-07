import asyncio
import logging
import random

from telethon import TelegramClient, events

from plugins.function import get_users


logger = logging.getLogger(__name__)


def setup(bot: TelegramClient, userbots: list[TelegramClient] | None = None):
    """Register /broadcast. The command must reply to the message to broadcast."""
    if userbots is None:
        userbots = []

    @bot.on(events.NewMessage(pattern=r"^/broadcast(?:@\w+)?$"))
    async def broadcast_command(event):
        try:
            if not event.is_reply:
                await event.respond(
                    "❌ /broadcast ko kisi message ke reply mein bhejo."
                )
                return

            reply = await event.get_reply_message()
            users = get_users()

            if not users:
                await event.respond(
                    "ℹ️ users.json mein koi subscribed user nahi hai."
                )
                return

            await event.respond(
                f"📢 Broadcast started.\n"
                f"👥 Recipients: {len(users)}"
            )

            sent = 0
            failed = 0

            for index, user_id in enumerate(users):
                if not userbots:
                    failed += 1
                    break

                try:
                    userbot = random.choice(userbots)
                    await userbot.send_message(int(user_id), reply)
                    sent += 1
                except Exception:
                    failed += 1
                    logger.exception(
                        "Broadcast failed for user_id=%s",
                        user_id,
                    )

                if index < len(users) - 1:
                    await asyncio.sleep(random.uniform(3, 9))

            await event.respond(
                "✅ Broadcast finished.\n"
                f"📨 Sent: {sent}\n"
                f"❌ Failed: {failed}"
            )

        except Exception:
            logger.exception("Error handling /broadcast.")
            await event.respond("❌ Broadcast failed.")
