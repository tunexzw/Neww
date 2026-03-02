# ---------------------------------------------------
# File Name: Verification.py
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import VERIFY, VERIFY_TUTORIAL, VERIFY_PIC
from database.db import db
from MyselfNeon.verify import get_token, check_verification


@Client.on_message(filters.private & filters.command(["verify"]))
async def verify_command_handler(bot, message):
    if await db.is_banned(message.from_user.id):
        return await message.reply(
            "🚫 <b>You are blocked due to suspicious activity.</b>\n\n"
            "<b>You cannot use this bot. Please contact admin for unban.</b>"
        )

    if not VERIFY:
        return await message.reply("♻️ <b>Verification is currently disabled.</b>")

    if await check_verification(message.from_user.id):
        return await message.reply("✅ <b>You are already verified for 4 hours.</b>")

    msg = await message.reply("<b>Please wait, generating your verification link...</b>")

    bot_info = await bot.get_me()
    start_link = f"https://t.me/{bot_info.username}?start="

    try:
        verify_url = await get_token(bot, message.from_user.id, start_link)
        buttons = [
            [InlineKeyboardButton("🔗 Click Here To Verify", url=verify_url)],
            [InlineKeyboardButton("❓ How To Verify", url=VERIFY_TUTORIAL)],
            [InlineKeyboardButton("💎 Premium Plans", callback_data="premium_btn")]
        ]

        if VERIFY_PIC:
            await msg.delete()
            await message.reply_photo(
                VERIFY_PIC,
                caption="<b>🔐 Verification Required!</b>\n\n<b>To continue using this bot, please verify your account.</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await msg.edit(
                text="<b>🔐 Verification Required!</b>\n\n"
                     "<b>To continue using this bot, please verify your account.</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        await msg.edit(f"<b>Error generating link:</b> <code>{e}</code>")


@Client.on_callback_query(filters.regex("verify_query"))
async def verify_callback(bot, query):
    if await db.is_banned(query.from_user.id):
        await query.answer("You are banned from using this bot.", show_alert=True)
        return

    await query.message.reply("<b>Use /verify to generate your verification link.</b>")
    await query.answer()
