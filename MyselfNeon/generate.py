# ---------------------------------------------------
# File Name: Generate.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# Created: 2025-10-21
# Last Modified: 2025-10-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.db import db

SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        return 
    await db.set_session(message.from_user.id, session=None)
    await message.reply("**__Logout Successfully__ 🚪**")

# --- NEW COMMAND: Login via Session String ---
@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login_session"]))
async def login_session_handler(bot: Client, message: Message):
    # 1. Check if user is already logged in
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**__You Are Already Logged In 🤓\n\nFirst /logout Your Old Session. Then Do /login_session Again !!__ 🔑**")
        return 

    # 2. Ask for the Session String
    try:
        sess_msg = await bot.ask(
            chat_id=message.from_user.id, 
            text="**__Please Send Your Pyrogram Session String__ 🎟️**\n\n__It usually starts with `BQ...`__\n__Type /cancel to cancel process.__", 
            filters=filters.text, 
            timeout=300
        )
    except TimeoutError:
        return await message.reply('**❌ __Time Limit Exceeded !!__**')
    
    if sess_msg.text == '/cancel':
        return await sess_msg.reply('<b>❌ __Process Cancelled !!__</b>')

    session_string = sess_msg.text.strip()

    # 3. Step 1: Immediate Format/Length Check
    if len(session_string) < 100: # Basic sanity check
        return await sess_msg.reply('**❌ __Invalid Session String Format (Too Short).__**')

    status_msg = await sess_msg.reply("**__🔄 Verifying Session Validity...__**")

    # 4. Step 2: Functional Check (Try to Connect)
    try:
        # We use :memory: to avoid creating a file, just testing the string
        temp_client = Client(":memory:", session_string=session_string, api_id=API_ID, api_hash=API_HASH)
        await temp_client.connect()
        me = await temp_client.get_me() # If this succeeds, the session is alive
        await temp_client.disconnect()

        # 5. Success: Save to Database
        await db.set_session(message.from_user.id, session=session_string)
        await status_msg.edit(f"**__✅ Login Successful!__**\n\n**Logged in as:** `{me.first_name}`")

    except Exception as e:
        # If connection failed (SessionInvalid, AuthKeyUnregistered, etc.)
        await status_msg.edit(f"**❌ __Session String Verification Failed!__**\n\n`{e}`")


# --- EXISTING COMMAND: Login via Phone Number ---
@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**__Your Are Already Logged In 🤓\n\nFirst /logout Your Old Session. Then Do /login Again !!__ 🔑**")
        return 
    user_id = int(message.from_user.id)
    phone_number_msg = await bot.ask(chat_id=user_id, text="<b>__Please Send Your Phone Number Which Includes Country Code__ 📊</b>\n\n<b>__Example:__</b> <code>+91987654321</code>")
    if phone_number_msg.text=='/cancel':
        return await phone_number_msg.reply('<b>❌ __Process Cancelled !!__</b>')
    phone_number = phone_number_msg.text
    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()
    await phone_number_msg.reply("**📩 __Sending OTP...__**")
    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(user_id, "**__Please Check for an OTP in Official Telegram Account. If you got it, Send OTP here after Reading the Below Format. \n\nIf OTP Is 12345\nPlease Send It As 1 2 3 4 5.\n\nEnter /cancel to Cancel The Procces__**", filters=filters.text, timeout=600)
    except PhoneNumberInvalid:
        await phone_number_msg.reply('**❌ __PHONE_NUMBER Is Invalid.__**')
        return
    if phone_code_msg.text=='/cancel':
        return await phone_code_msg.reply('<b>❌ __Process Cancelled !!__</b>')
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**❌ __OTP Is Invalid.__**')
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**❌ __OTP Is Expired.__**')
        return
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(user_id, '**__Your Account has Enabled Two-step Verification. Please Provide the Password.\n\nEnter /cancel to Cancel The Procces__**', filters=filters.text, timeout=300)
        if two_step_msg.text=='/cancel':
            return await two_step_msg.reply('<b>❌ __Process Cancelled !!__</b>')
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('**❌ __Invalid Password Provided__**')
            return
    string_session = await client.export_session_string()
    await client.disconnect()
    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>❌ __Invalid Session Sring__</b>')
    try:
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            uclient = Client(":memory:", session_string=string_session, api_id=API_ID, api_hash=API_HASH)
            await uclient.connect()
            await db.set_session(message.from_user.id, session=string_session)
    except Exception as e:
        return await message.reply_text(f"<b>❌ __ERROR IN LOGIN: `{e}`__</b>")
    await bot.send_message(message.from_user.id, "<b>__Account Login Successfully ✅\n\nIf You Get Any Error Related To AUTH KEY Then /logout first and /login again.__</b>")

# Dont remove Credits
# Developer Telegram @MyselfNeon
# Update channel - @NeonFiles
