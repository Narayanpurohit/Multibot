# config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Telegram API
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# Owner
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Default Chat
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

# Userbot Accounts
USERBOT_ACCOUNTS = [
    account.strip()
    for account in os.getenv("USERBOT_ACCOUNTS", "").split(",")
    if account.strip()
]
