# ---------------------------------------------------
# File Name: DB.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# YouTube: https://youtube.com/@MyselfNeon
# Created: 2025-10-21
# Last Modified: 2025-10-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

import motor.motor_asyncio
from datetime import datetime, timezone, timedelta
from config import DB_NAME, DB_URI


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name, username):
        return dict(
            id=id,
            name=name,
            username=username,
            session=None,
            verify_token=None,
            verify_date=None,
            verify_issued_at=None,
            verify_bypass_attempts=0,
            is_banned=False,
            premium_tier="free",
            premium_expires_at=None,
            batch_daily_count=0,
            batch_daily_date=None,
            last_save_at=None,
            destination_chat_id=None
        )

    async def add_user(self, id, name, username):
        user = self.new_user(id, name, username)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session') if user else None

    async def update_verify_token(self, id, token):
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'verify_token': token, 'verify_issued_at': datetime.now(timezone.utc)}},
            upsert=True
        )

    async def get_verify_token(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('verify_token') if user else None

    async def clear_verify_token(self, id):
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'verify_token': None, 'verify_issued_at': None}},
            upsert=True
        )

    async def update_verify_date(self, id, date):
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'verify_date': date, 'verify_token': None, 'verify_issued_at': None}}
        )

    async def get_verify_date(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('verify_date') if user else None

    async def get_verify_issued_at(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('verify_issued_at') if user else None

    async def reset_verify_time(self, id):
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'verify_date': None, 'verify_token': None, 'verify_issued_at': None}},
            upsert=True
        )

    async def increment_verify_bypass_attempt(self, id):
        await self.col.update_one({'id': int(id)}, {'$inc': {'verify_bypass_attempts': 1}}, upsert=True)
        user = await self.col.find_one({'id': int(id)})
        return int(user.get('verify_bypass_attempts', 0)) if user else 0

    async def reset_verify_bypass_attempt(self, id):
        await self.col.update_one({'id': int(id)}, {'$set': {'verify_bypass_attempts': 0}}, upsert=True)

    async def get_user(self, id):
        return await self.col.find_one({'id': int(id)})

    async def ensure_user(self, id, name=None, username=None):
        if not await self.is_user_exist(id):
            await self.add_user(id, name or "User", username)

    async def set_premium(self, id, tier, days):
        expires_at = datetime.now(timezone.utc) + timedelta(days=int(days))
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'premium_tier': tier, 'premium_expires_at': expires_at}},
            upsert=True
        )
        return expires_at

    async def remove_premium(self, id):
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'premium_tier': 'free', 'premium_expires_at': None}},
            upsert=True
        )

    async def get_active_tier(self, id):
        user = await self.get_user(id)
        if not user:
            return "free", None

        tier = user.get("premium_tier", "free")
        expires_at = user.get("premium_expires_at")

        if tier in ("pro", "pro_gold") and expires_at:
            now_utc = datetime.now(timezone.utc)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if now_utc < expires_at:
                return tier, expires_at

        return "free", None

    async def get_batch_daily_count(self, id):
        user = await self.get_user(id)
        if not user:
            return 0
        today = datetime.now(timezone.utc).date().isoformat()
        if user.get("batch_daily_date") != today:
            await self.col.update_one(
                {'id': int(id)},
                {'$set': {'batch_daily_date': today, 'batch_daily_count': 0}}
            )
            return 0
        return int(user.get("batch_daily_count", 0))

    async def increment_batch_daily_count(self, id, value=1):
        await self.get_batch_daily_count(id)
        await self.col.update_one({'id': int(id)}, {'$inc': {'batch_daily_count': int(value)}})

    async def get_last_save_at(self, id):
        user = await self.get_user(id)
        if not user:
            return None
        return user.get("last_save_at")

    async def set_last_save_at(self, id):
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'last_save_at': datetime.now(timezone.utc)}},
            upsert=True
        )


    async def set_destination_chat(self, id, chat_id):
        await self.col.update_one(
            {'id': int(id)},
            {'$set': {'destination_chat_id': int(chat_id)}},
            upsert=True
        )

    async def get_destination_chat(self, id):
        user = await self.get_user(id)
        if not user:
            return None
        return user.get('destination_chat_id')

    async def set_ban_status(self, id, banned: bool):
        await self.col.update_one({'id': int(id)}, {'$set': {'is_banned': bool(banned)}}, upsert=True)

    async def is_banned(self, id):
        user = await self.get_user(id)
        return bool(user.get('is_banned', False)) if user else False


db = Database(DB_URI, DB_NAME)
