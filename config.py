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

# Groups where the userbot should process incoming messages.
# .env example: A_CHAT_ID=-1001234567890,-1009876543210
A_CHAT_ID = [
    int(chat_id.strip())
    for chat_id in os.getenv("A_CHAT_ID", "").split(",")
    if chat_id.strip()
]

# Userbot Session Strings
# Keep real session strings only in .env, never in this public file.
USERBOT_SESSIONS = [
    os.getenv("USERBOT_SESSION_1", ""),
    os.getenv("USERBOT_SESSION_2", ""),
    os.getenv("USERBOT_SESSION_3", ""),
    os.getenv("USERBOT_SESSION_4", ""),
    os.getenv("USERBOT_SESSION_5", ""),
    os.getenv("USERBOT_SESSION_6", ""),
    
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
