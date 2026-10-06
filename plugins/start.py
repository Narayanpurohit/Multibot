from pyrogram import filters
from pyrogram.types import Message


def setup(bot):
    @bot.on_message(filters.command("start"))
    async def start_command(client, message: Message):
        await message.reply_text(
            f"Hello {message.from_user.first_name}! 👋\n"
            "Bot is online and ready."
        )
