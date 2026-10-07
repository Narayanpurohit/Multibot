import asyncio
import importlib
import logging
import os

from telethon import TelegramClient

from config import API_ID, API_HASH, BOT_TOKEN, USERBOT_ACCOUNTS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("multibot")


# Plugins currently available in the half-code build.
# Broadcast will be added later.
PLUGIN_MODULES = [
    "plugins.start",
    "plugins.function",
    "plugins.stats",
]


def load_plugins(bot: TelegramClient):
    """Load and initialize bot plugins."""
    for module_name in PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_name)
            setup = getattr(module, "setup", None)

            if setup:
                setup(bot)
                logger.info("Loaded plugin: %s", module_name)
            else:
                logger.warning("No setup() found in plugin: %s", module_name)

        except Exception:
            logger.exception("Failed to load plugin: %s", module_name)
            raise


def create_userbot(account: str) -> TelegramClient:
    """Create a Telethon client for a configured user account."""
    return TelegramClient(
        os.path.join("sessions", account),
        API_ID,
        API_HASH,
    )


async def main():
    os.makedirs("sessions", exist_ok=True)

    # Main Telegram bot.
    bot = TelegramClient(
        os.path.join("sessions", "bot"),
        API_ID,
        API_HASH,
    )

    # Userbot accounts.
    userbots = [
        create_userbot(account)
        for account in USERBOT_ACCOUNTS
    ]

    try:
        # Start bot using the configured bot token.
        await bot.start(bot_token=BOT_TOKEN)
        logger.info("Bot started successfully.")

        # Start all userbot accounts.
        for index, userbot in enumerate(userbots, start=1):
            try:
                await userbot.start()
                logger.info("Userbot account %d started.", index)
            except Exception:
                logger.exception(
                    "Failed to start userbot account %d.",
                    index,
                )
                raise

        # Register bot plugins.
        load_plugins(bot)

        # Register userbot handlers.
        from userbot.userbot import setup_all

        setup_all(userbots)

        logger.info(
            "All clients started. Userbots: %d",
            len(userbots),
        )

        # Keep all Telethon clients running.
        await asyncio.Event().wait()

    except Exception:
        logger.exception("Fatal error while running Multibot.")
        raise

    finally:
        for index, userbot in enumerate(userbots, start=1):
            try:
                if userbot.is_connected():
                    await userbot.disconnect()
                    logger.info(
                        "Userbot account %d stopped.",
                        index,
                    )
            except Exception:
                logger.exception(
                    "Error stopping userbot account %d.",
                    index,
                )

        try:
            if bot.is_connected():
                await bot.disconnect()
                logger.info("Bot stopped.")
        except Exception:
            logger.exception("Error stopping bot.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")
