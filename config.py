# ---------------------------------------------------
# File Name: Config.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# Created: 2025-11-21
# Last Modified: 2025-11-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

import os

# Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Port for Web Server
PORT = int(os.environ.get("PORT", "8080"))

# Your API ID & Hash
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", ""))

# Your Mongodb Database Url
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "SaveRestricted")

# Log Channel to Track New Users 
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))

# Dump Channel for File Tracking (ADDED)
DUMP_CHANNEL = int(os.environ.get("DUMP_CHANNEL", ""))

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then False
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))

# Keep-Alive URL
KEEP_ALIVE_URL = os.environ.get("KEEP_ALIVE_URL", "https://snaplover-c0ft.onrender.com")

# Start pic on /start 
START_PIC = os.environ.get("START_PIC", "https://i.ibb.co/VchKdpT7/bb96e5669bb2.jpg")

# Force Subscribe Channel (set 0 to disable)
FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", "-1003870553259"))
FORCE_SUB_CHANNEL_URL = os.environ.get("FORCE_SUB_CHANNEL_URL", "https://t.me/TuneBots")

# Optional UI Photos
VERIFY_PIC = os.environ.get("VERIFY_PIC", "https://i.ibb.co/b50cM7rV/7b66c8c6a794.jpg")
MY_PLAN_PIC = os.environ.get("MY_PLAN_PIC", "https://i.ibb.co/27ddyYWT/f3d831637fb7.jpg")
FORCE_SUB_PIC = os.environ.get("FORCE_SUB_PIC", "https://i.ibb.co/217xYszg/09b02ff28bcf.jpg")
BYPASS_ALERT_PIC = os.environ.get("BYPASS_ALERT_PIC", "https://i.ibb.co/qL3tbFrp/d293604f2128.jpg")
AUTO_DELETE_SECONDS = int(os.environ.get("AUTO_DELETE_SECONDS", "600"))

# -------------------
# VERIFICATION CONFIG
# -------------------
VERIFY = bool(os.environ.get('VERIFY', True)) # Set True to enable
VERIFY_SHORTLINK_URL = os.environ.get('VERIFY_SHORTLINK_URL', '') # Your Shortener Domain
VERIFY_SHORTLINK_API = os.environ.get('VERIFY_SHORTLINK_API', '') # Your Shortener API Key
VERIFY_TUTORIAL = os.environ.get('VERIFY_TUTORIAL', 'https://t.me/your_tutorial_link') # Tutorial Link

VERIFY_MIN_SECONDS = int(os.environ.get("VERIFY_MIN_SECONDS", ""))
VERIFY_BYPASS_BAN_ATTEMPTS = int(os.environ.get("VERIFY_BYPASS_BAN_ATTEMPTS", ""))

# -------------------
# PREMIUM CONFIG
# -------------------
FREE_SAVE_COOLDOWN_SECONDS = int(os.environ.get("FREE_SAVE_COOLDOWN_SECONDS", ""))
PRO_DAILY_BATCH_LIMIT = int(os.environ.get("PRO_DAILY_BATCH_LIMIT", ""))

PREMIUM_OVERVIEW_TEXT = os.environ.get(
    "PREMIUM_OVERVIEW_TEXT",
    "<b>💎 Premium Plans</b>\n\n"
    "<b><blockquote>𝙁𝙧𝙚𝙚:</b>\n𝘾𝙤𝙤𝙡𝙙𝙤𝙬𝙣 𝙏𝙞𝙢𝙚: 1 ᴍɪɴᴜᴛᴇ\n 𝙑𝙚𝙧𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣: Rᴇǫᴜɪʀᴇᴅ.\n 𝘽𝙖𝙩𝙘𝙝 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 𝘼𝙘𝙘𝙚𝙨𝙨: Nᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ.</blockquote></b>\n"
    "<b><blockquote>𝙋𝙧𝙤:</b>\n𝘾𝙤𝙤𝙡𝙙𝙤𝙬𝙣 𝙏𝙞𝙢𝙚: Nᴏɴᴇ\n 𝙑𝙚𝙧𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣: Rᴇǫᴜɪʀᴇᴅ\n 𝘽𝙖𝙩𝙘𝙝 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 𝘼𝙘𝙘𝙚𝙨𝙨: 350 ᴍᴇssᴀɢᴇs ᴅᴀɪʟʏ.</blockquote>\n"
    "<b><blockquote>𝙋𝙧𝙤 𝙂𝙤𝙡𝙙:</b>\n 𝘾𝙤𝙤𝙡𝙙𝙤𝙬𝙣 𝙏𝙞𝙢𝙚: Nᴏɴᴇ\n 𝙑𝙚𝙧𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣: Nᴏᴛ ʀᴇǫᴜɪʀᴇᴅ \n 𝘽𝙖𝙩𝙘𝙝 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 𝘼𝙘𝙘𝙚𝙨𝙨: Uɴʟɪᴍɪᴛᴇᴅ.</blockquote>"
)

PRO_PLAN_NAME = os.environ.get("PRO_PLAN_NAME", "PRO PLAN")
PRO_PLAN_QR_IMAGE = os.environ.get("PRO_PLAN_QR_IMAGE", "")
PRO_PLAN_DETAILS = os.environ.get(
    "PRO_PLAN_DETAILS",
    "<blockquote>👑 PRO PLAN – ₹100\n\n"
    "🔥 Uʟᴛɪᴍᴀᴛᴇ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss:\n\n"
    "✅ Nᴏ Cᴏᴏʟᴅᴏᴡɴ Tɪᴍᴇ\n"
    "✅ Vᴇʀɪғɪᴄᴀᴛɪᴏɴ Rᴇǫᴜɪʀᴇᴅ\n"
    "✅ 350 Bᴀᴛᴄʜ Mᴇssᴀɢᴇ Sᴀᴠɪɴɢ\n"
    "✅ Fᴀsᴛᴇsᴛ Pʀᴏᴄᴇssɪɴɢ Sᴘᴇᴇᴅ\n"
    "✅ Fᴜʟʟ Bᴏᴛ Aᴄᴄᴇss\n"
    "✅ Pʀɪᴏʀɪᴛʏ Sᴜᴘᴘᴏʀᴛ\n\n"
    "💳 Pᴀʏᴍᴇɴᴛ Mᴇᴛʜᴏᴅ\n\n"
    "UPI ID: luciferjaat@ptyes\n"
    "Pᴀʏ ᴜsɪɴɢ UPI / GPᴀʏ / PʜᴏɴᴇPᴇ / Pᴀʏᴛᴍ\n\n"
    "📌 Aғᴛᴇʀ Pᴀʏᴍᴇɴᴛ:\n"
    "Sᴇɴᴅ Pᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ ᴛᴏ Aᴅᴍɪɴ ғᴏʀ Iɴsᴛᴀɴᴛ Aᴄᴛɪᴠᴀᴛɪᴏɴ.</blockquote>"
)

PRO_GOLD_PLAN_NAME = os.environ.get("PRO_GOLD_PLAN_NAME", "PRO GOLD PLAN")
PRO_GOLD_PLAN_QR_IMAGE = os.environ.get("PRO_GOLD_PLAN_QR_IMAGE", "")
PRO_GOLD_PLAN_DETAILS = os.environ.get(
    "PRO_GOLD_PLAN_DETAILS",
    "<blockquote>👑 PRO GOLD PLAN – ₹200\n\n"
    "🔥 Uʟᴛɪᴍᴀᴛᴇ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss:\n\n"
    "✅ Nᴏ Cᴏᴏʟᴅᴏᴡɴ Tɪᴍᴇ\n"
    "✅ Nᴏ Vᴇʀɪғɪᴄᴀᴛɪᴏɴ Rᴇǫᴜɪʀᴇᴅ\n"
    "✅ Uɴʟɪᴍɪᴛᴇᴅ Bᴀᴛᴄʜ Mᴇssᴀɢᴇ Sᴀᴠɪɴɢ\n"
    "✅ Fᴀsᴛᴇsᴛ Pʀᴏᴄᴇssɪɴɢ Sᴘᴇᴇᴅ\n"
    "✅ Fᴜʟʟ Bᴏᴛ Aᴄᴄᴇss\n"
    "✅ Pʀɪᴏʀɪᴛʏ Sᴜᴘᴘᴏʀᴛ\n\n"
    "💳 Pᴀʏᴍᴇɴᴛ Mᴇᴛʜᴏᴅ\n\n"
    "UPI ID: luciferjaat@ptyes\n"
    "Pᴀʏ ᴜsɪɴɢ UPI / GPᴀʏ / PʜᴏɴᴇPᴇ / Pᴀʏᴛᴍ\n\n"
    "📌 Aғᴛᴇʀ Pᴀʏᴍᴇɴᴛ:\n"
    "Sᴇɴᴅ Pᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ ᴛᴏ Aᴅᴍɪɴ ғᴏʀ Iɴsᴛᴀɴᴛ Aᴄᴛɪᴠᴀᴛɪᴏɴ.</blockquote>"
)

PREMIUM_CONTACT_BUTTON_TEXT = os.environ.get("PREMIUM_CONTACT_BUTTON_TEXT", "📞 Contact Admin")
PREMIUM_CONTACT_URL = os.environ.get("PREMIUM_CONTACT_URL", "")

PRO_PLAN_DETAILS_FROM_ENV = "PRO_PLAN_DETAILS" in os.environ
PRO_GOLD_PLAN_DETAILS_FROM_ENV = "PRO_GOLD_PLAN_DETAILS" in os.environ
PREMIUM_OVERVIEW_TEXT_FROM_ENV = "PREMIUM_OVERVIEW_TEXT" in os.environ

# MyselfNeon
# Don't Remove Credit 🥺
# Telegram Channel @NeonFiles
