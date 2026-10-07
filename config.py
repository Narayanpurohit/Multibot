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
    "userbot1",
    "userbot2",
]

# Newsletter Messages
NS1 = """◈ **ʜᴇʏ ʙʀᴏ 👋**

ᴍᴇɴᴇ ᴇᴋ **ꜱʜᴏʀᴛɴᴇʀ ʙʏᴘᴀꜱꜱ ʙᴏᴛ** ʙᴀɴᴀʏᴀ ʜᴀɪ 😎 ᴛʀʏ ᴋᴀʀᴏɢᴇ?

⛓ **@url_bypasser_jnbot**

✯ ɴᴇᴡ ᴜᴘᴅᴀᴛᴇꜱ ᴘᴀɴᴇ ᴋᴇ ʟɪʏᴇ → `/subscribe` × ɴᴇᴡꜱʟᴇᴛᴛᴇʀ ꜱᴛᴏᴘ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ → `/stop`"""

NS2 = """◈ ɴᴇᴡꜱʟᴇᴛᴛᴇʀ

ʜᴇʏ 👋
ᴍᴇɴᴇ ᴇᴋ ꜱʜᴏʀᴛɴᴇʀ ʙʏᴘᴀꜱꜱ ʙᴏᴛ ʙᴀɴᴀʏᴀ ʜᴀɪ — ᴛʀʏ ᴋᴀʀᴏɢᴇ? 😉

⛓ ʙᴏᴛ: @url_bypasser_jnbot

━━━━━━━━━━━━━━━━━━

✯ ɴᴇᴡꜱ & ᴜᴘᴅᴀᴛᴇꜱ ᴘᴀɴᴇ ᴋᴇ ʟɪʏᴇ:
`/subscribe`

⍟ ɴᴇᴡꜱʟᴇᴛᴛᴇʀ ꜱᴛᴏᴘ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ:
`/stop`"""

NS3 = """◈ ɪɴᴛʀᴏᴅᴜᴄɪɴɢ ᴍʏ ꜱʜᴏʀᴛɴᴇʀ ʙʏᴘᴀꜱꜱ ʙᴏᴛ 🚀

ᴜʀʟ ʜᴀɪ? ʙᴏᴛ ᴋᴏ ꜱᴇɴᴅ ᴋᴀʀᴏ ᴀɴᴅ ʟᴇᴛ'ꜱ ꜱᴇᴇ ᴡʜᴀᴛ ɪᴛ ᴄᴀɴ ᴅᴏ. 😉

⛓ @url_bypasser_jnbot

⍟ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀʜɪʏᴇ? `/subscribe`
× ꜱᴛᴏᴘ ᴋᴀʀɴᴀ ʜᴀɪ? `/stop`"""

NS4 = """◈ ɪɴᴛʀᴏᴅᴜᴄɪɴɢ — ᴜʀʟ ʙʏᴘᴀꜱꜱᴇʀ

ᴀ ꜱɪᴍᴘʟᴇ ᴀɴᴅ ꜰᴀꜱᴛ ᴡᴀʏ ᴛᴏ ᴛʀʏ ᴏᴜʀ ꜱʜᴏʀᴛɴᴇʀ ʙʏᴘᴀꜱꜱ ʙᴏᴛ.

↗ @url_bypasser_jnbot

✯ ꜱᴜʙꜱᴄʀɪʙᴇ: `/subscribe`
× ᴜɴꜱᴜʙꜱᴄʀɪʙᴇ: `/stop`"""
