import asyncio
import importlib
import os

from pyrogram import Client, idle

from config import API_ID, API_HASH, BOT_TOKEN, USERBOT_ACCOUNTS


PLUGIN_MODULES = [
    "plugins.start",
    "plugins.function",
    "plugins.broadcast",
]


def load_plugins(bot: Client):
    for module_name in PLUGIN_MODULES:
        module = importlib.import_module(module_name)

        setup = getattr(module, "setup", None)
        if setup:
            setup(bot)


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

    await bot.start()

    for userbot in userbots:
        await userbot.start()

    print("Bot started.")
    print(f"Userbot accounts started: {len(userbots)}")

    await idle()

    for userbot in userbots:
        await userbot.stop()

    await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
