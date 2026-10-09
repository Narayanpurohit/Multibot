import logging

from telethon import TelegramClient, events

from config import A_CHAT_ID
from plugins.function import (
    add_user,
    is_user_pending,
    mark_userbot_for_user,
    notify_owner,
    process_permission_message,
    remove_user,
    save_resolved_peer,
)

logger = logging.getLogger(__name__)


def setup(
    userbot: TelegramClient,
    userbots: list[TelegramClient] | None = None,
    userbot_index: int = 1,
):
    """Register incoming-group and subscription handlers for one userbot."""
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
                    "✅ You are subscribed."
                    if added else "ℹ️ You are already subscribed."
                )
            else:
                removed = remove_user(user_id)
                await event.respond(
                    "🛑 You have been unsubscribed."
                    if removed else "ℹ️ You are not subscribed."
                )
        except Exception as error:
            logger.exception("Error handling subscription command.")
            await notify_owner(
                f"❌ Subscription handler error\n"
                f"Error: {type(error).__name__}: {error}",
                userbots,
            )

    @userbot.on(events.NewMessage(incoming=True))
    async def incoming_group_message(event):
        try:
            if not event.is_group or event.chat_id not in A_CHAT_ID:
                return

            sender = await event.get_sender()
            if not sender or getattr(sender, "bot", False):
                return

            user_id = int(sender.id)
            try:
                input_peer = await event.get_input_sender()
                if input_peer is None:
                    raise ValueError("Telegram did not return an input peer")
                if not save_resolved_peer(user_id, userbot_index, input_peer):
                    raise ValueError("Could not persist the resolved input peer")
                mark_userbot_for_user(user_id, userbot_index)
            except Exception as error:
                logger.exception("Failed to resolve/save peer for user_id=%s", user_id)
                await notify_owner(
                    f"❌ Peer/entity error\nUser ID: {user_id}\n"
                    f"Userbot: {userbot_index}\n"
                    f"Error: {type(error).__name__}: {error}",
                    userbots,
                )
                return

            # pending.json tracks users already sent a permission prompt.
            if is_user_pending(user_id):
                return

            await process_permission_message(user_id, userbots)

        except Exception as error:
            logger.exception("Error handling incoming group message.")
            await notify_owner(
                f"❌ Group handler error\n"
                f"User ID: {locals().get('user_id', 'unknown')}\n"
                f"Userbot: {userbot_index}\n"
                f"Error: {type(error).__name__}: {error}",
                userbots,
            )


def setup_all(userbots: list[TelegramClient]):
    """Register handlers on every configured userbot account."""
    if not userbots:
        logger.warning("No userbot accounts are configured.")
        return
    if not A_CHAT_ID:
        logger.warning("A_CHAT_ID is empty. No group messages will be processed.")

    for index, userbot in enumerate(userbots, start=1):
        setup(userbot, userbots, userbot_index=index)
        logger.info("Userbot group-message handler loaded for account %d.", index)
