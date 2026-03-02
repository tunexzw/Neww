# ---------------------------------------------------
# File Name: Bot.py
# Author: NeonAnurag
# Original Repo: https://github.com/MyselfNeon/SaveRestrictions-Bot
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# Created: 2025-11-21
# ---------------------------------------------------

import asyncio
import logging
import datetime
from datetime import timezone, timedelta
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient  # ✅ MongoDB
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, KEEP_ALIVE_URL, DB_URI, DB_NAME

# ✅ Indian Standard Time
IST = timezone(timedelta(hours=5, minutes=30))

# ✅ MongoDB Setup
mongo_client = AsyncIOMotorClient(DB_URI)
db = mongo_client[DB_NAME]
users_col = db["logged_users"]

async def keep_alive():
    """Send a request every 100 seconds to keep the bot alive."""
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(KEEP_ALIVE_URL)
                logging.info("Sent keep-alive request.")
            except Exception as e:
                logging.error(f"Keep-alive request failed: {e}")
            await asyncio.sleep(100)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "Neon Login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="MyselfNeon"),
            workers=50,
            sleep_threshold=10
        )
        self.keep_alive_task = None

    async def start(self):
        await super().start()
        me = await self.get_me()

        # 🔍 Debug MongoDB connection
        print(f"[✅] Connected to MongoDB DB: {db.name}")
        print(f"[✅] Using Collection: {users_col.name}")
        count = await users_col.count_documents({})
        print(f"[✅] Current Stored Users: {count}")

        # Start keep-alive
        self.keep_alive_task = asyncio.create_task(keep_alive())

        # Bot startup log
        now = datetime.datetime.now(IST)
        date = now.strftime("%d/%m/%y")
        time = now.strftime("%I:%M:%S %p")
        text = (
            f"**⌬ Restarted Successfully !**\n"
            f"**┟ Bot:** __@{me.username}__\n"
            f"**┟ Date:** __{date}__\n"
            f"**┠ Time:** __{time}__\n"
            f"**┠ TimeZone:** __Asia/Kolkata__\n"
            f"**┖ Version:** __v3.0.8-x__"
        )
        try:
            await self.send_message(LOG_CHANNEL, text)
        except Exception as e:
            print(f"Log send failed: {e}")

        print(f"✅ Bot Powered By @{me.username}")

    async def stop(self, *args):
        me = await self.get_me()

        # Stop keep-alive loop
        if self.keep_alive_task:
            self.keep_alive_task.cancel()
            try:
                await self.keep_alive_task
            except asyncio.CancelledError:
                pass

        try:
            await self.send_message(LOG_CHANNEL, f"❌ Bot @{me.username} Stopped")
        except Exception as e:
            print(f"Stop log failed: {e}")

        await super().stop()
        print("Bot Stopped — Bye 👋")

BotInstance = Bot()

# ✅ User Logging Handler (Persistent MongoDB)
@BotInstance.on_message(filters.private & filters.incoming, group=-1)
async def new_user_log(bot: Client, message: Message):
    user = message.from_user
    if not user:
        return

    now = datetime.datetime.now(IST)

    # ✅ Use UPSERT to avoid duplicate registration
    result = await users_col.update_one(
        {"user_id": user.id},
        {"$setOnInsert": {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "logged_at": now.isoformat()
        }},
        upsert=True
    )

    # Log only when it's a *new* user
    if result.upserted_id:
        date = now.strftime("%d/%m/%y")
        time = now.strftime("%I:%M.%S %p") # ✅ Format: 01:37.08 PM
        
        text = (
            f"**⌬ 🆕👤 #NewUser** \n"
            f"**┟ Bot:** __@{bot.me.username}__\n"
            f"**┟ User:** __{user.mention}__\n"
            f"**┟ User ID:** <code>{user.id}</code>\n"
            f"**┟ Date:** __{date}__\n"
            f"**┖ Time:** __{time}__"
        )
        try:
            await bot.send_message(LOG_CHANNEL, text)
        except Exception as e:
            print(f"New user log failed: {e}")

BotInstance.run()

# MyselfNeon
# Don't Remove Credit 🥺
# Telegram Channel @NeonFiles
