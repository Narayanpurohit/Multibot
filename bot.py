import asyncio
import importlib
import logging
import os

from pyrogram import Client, idle

from config import API_ID, API_HASH, BOT_TOKEN, USERBOT_ACCOUNTS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("multibot")


PLUGIN_MODULES = [
    "plugins.start",
    "plugins.function",
    "plugins.broadcast",
]


def load_plugins(bot: Client):
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


def create_userbot(account: str) -> Client:
    return Client(
        name=account,
        api_id=API_ID,
        api_hash=API_HASH,
        workdir="sessions",
    )


async def main():
    os.makedirs("sessions", exist_ok=True)

    bot = Client(
        "bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )

    load_plugins(bot)

    userbots = [
        create_userbot(account)
        for account in USERBOT_ACCOUNTS
    ]

    try:
        await bot.start()
        logger.info("Bot started successfully.")

        for index, userbot in enumerate(userbots, start=1):
            try:
                await userbot.start()
                logger.info("Userbot account %d started.", index)
            except Exception:
                logger.exception("Failed to start userbot account %d.", index)
                raise

        logger.info("All clients started. Userbots: %d", len(userbots))

        await idle()

    except Exception:
        logger.exception("Fatal error while running Multibot.")
        raise

    finally:
        for index, userbot in enumerate(userbots, start=1):
            try:
                if userbot.is_connected:
                    await userbot.stop()
                    logger.info("Userbot account %d stopped.", index)
            except Exception:
                logger.exception("Error stopping userbot account %d.", index)

        try:
            if bot.is_connected:
                await bot.stop()
                logger.info("Bot stopped.")
        except Exception:
            logger.exception("Error stopping bot.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")
