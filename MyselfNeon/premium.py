from datetime import datetime, timezone, timedelta
from html import escape
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from config import (
    ADMINS, PREMIUM_OVERVIEW_TEXT, PRO_PLAN_NAME, PRO_PLAN_QR_IMAGE, PRO_PLAN_DETAILS,
    PRO_GOLD_PLAN_NAME, PRO_GOLD_PLAN_QR_IMAGE, PRO_GOLD_PLAN_DETAILS,
    PREMIUM_CONTACT_BUTTON_TEXT, PREMIUM_CONTACT_URL, MY_PLAN_PIC,
    PRO_PLAN_DETAILS_FROM_ENV, PRO_GOLD_PLAN_DETAILS_FROM_ENV, PREMIUM_OVERVIEW_TEXT_FROM_ENV
)
from database.db import db

IST = timezone(timedelta(hours=5, minutes=30))

BAN_TEXT = (
    "🚫 <b>You are blocked due to suspicious activity.</b>\n\n"
    "<b>You cannot use this bot. Please contact admin for unban.</b>"
)


def premium_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Pro Plan", callback_data="plan_pro"),
            InlineKeyboardButton("👑 Pro Gold", callback_data="plan_pro_gold")
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="start_btn")]
    ])


@Client.on_message(filters.command(["premium"]) & filters.private)
async def premium_command(client, message):
    if await db.is_banned(message.from_user.id):
        return await message.reply_text(BAN_TEXT)
    await message.reply_text(PREMIUM_OVERVIEW_TEXT, reply_markup=premium_keyboard(), disable_web_page_preview=True)




@Client.on_message(filters.command(["premium_debug"]) & filters.private)
async def premium_debug(client, message):
    if message.from_user.id != ADMINS:
        return await message.reply_text("❌ <b>Only admin can use this command.</b>")

    debug_text = (
        "<b>Premium Text Debug</b>\n\n"
        f"<b>PREMIUM_OVERVIEW_TEXT source:</b> <code>{'env' if PREMIUM_OVERVIEW_TEXT_FROM_ENV else 'config default'}</code>\n"
        f"<b>PRO_PLAN_DETAILS source:</b> <code>{'env' if PRO_PLAN_DETAILS_FROM_ENV else 'config default'}</code>\n"
        f"<b>PRO_GOLD_PLAN_DETAILS source:</b> <code>{'env' if PRO_GOLD_PLAN_DETAILS_FROM_ENV else 'config default'}</code>\n\n"
        f"<b>PRO_PLAN_DETAILS preview:</b>\n<code>{escape(PRO_PLAN_DETAILS[:350])}</code>"
    )
    await message.reply_text(debug_text, disable_web_page_preview=True)


@Client.on_message(filters.command(["my_plan"]) & filters.private)
async def my_plan(client, message):
    if await db.is_banned(message.from_user.id):
        return await message.reply_text(BAN_TEXT)

    tier, expires_at = await db.get_active_tier(message.from_user.id)
    destination_chat = await db.get_destination_chat(message.from_user.id)

    if tier == "free":
        text = "🆓 <b>Your Plan: FREE</b>\n\n<b>Upgrade using /premium.</b>"
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Set Destination Chat", callback_data="set_dest_chat")]])
        if MY_PLAN_PIC:
            return await message.reply_photo(MY_PLAN_PIC, caption=text, reply_markup=btn)
        return await message.reply_text(text, reply_markup=btn)

    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    total_seconds = max(0, int((expires_at - now).total_seconds()))

    text = (
        f"💎 <b>Your Plan: {tier.upper()}</b>\n"
        f"👤 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"📅 <b>Expiry:</b> <code>{expires_at.astimezone(IST).strftime('%d %b %Y, %I:%M %p IST')}</code>\n"
        f"⏳ <b>Remaining:</b> <code>{total_seconds // 86400}d {(total_seconds % 86400)//3600}h {(total_seconds % 3600)//60}m</code>\n"
        f"📥 <b>Destination Chat:</b> <code>{destination_chat if destination_chat else 'Not set'}</code>"
    )
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Set Destination Chat", callback_data="set_dest_chat")]])

    if MY_PLAN_PIC:
        return await message.reply_photo(MY_PLAN_PIC, caption=text, reply_markup=btn)
    await message.reply_text(text, reply_markup=btn)


@Client.on_callback_query(filters.regex("^set_dest_chat$"))
async def set_dest_chat_callback(client, query):
    if await db.is_banned(query.from_user.id):
        await query.answer("You are banned from using this bot.", show_alert=True)
        return

    tier, _ = await db.get_active_tier(query.from_user.id)
    if tier != "pro_gold":
        await query.answer("This feature is only for PRO GOLD users. Please upgrade.", show_alert=True)
        return

    await query.answer()
    ask_msg = await client.ask(
        chat_id=query.from_user.id,
        text="<b>Send the destination channel/chat ID where you want saved content.</b>\n\n"
             "<b>Important:</b> Bot must be admin there.",
        filters=filters.text,
        timeout=180
    )

    try:
        destination_chat_id = int(ask_msg.text.strip())
    except Exception:
        return await ask_msg.reply_text("❌ <b>Invalid chat ID.</b>")

    me = await client.get_me()
    try:
        member = await client.get_chat_member(destination_chat_id, me.id)
        status = str(getattr(member, "status", "")).lower()
        allowed = {"administrator", "creator", "chatmemberstatus.administrator", "chatmemberstatus.owner"}
        if status not in allowed:
            return await ask_msg.reply_text("❌ <b>Please make the bot admin in that chat, then try again.</b>")
    except UserNotParticipant:
        return await ask_msg.reply_text("❌ <b>Bot is not in that chat. Add the bot as admin first.</b>")
    except Exception as e:
        return await ask_msg.reply_text(f"❌ <b>Unable to validate chat:</b> <code>{e}</code>")

    await db.set_destination_chat(query.from_user.id, destination_chat_id)
    await ask_msg.reply_text(f"✅ <b>Destination chat saved:</b> <code>{destination_chat_id}</code>")


@Client.on_message(filters.command(["add_premium_pro", "add_premium_gold"]) & filters.private)
async def add_premium(client, message):
    if message.from_user.id != ADMINS:
        return await message.reply_text("❌ <b>Only admin can use this command.</b>")
    if len(message.command) != 3:
        return await message.reply_text(f"<b>Usage:</b> <code>/{message.command[0]} userid days</code>")
    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
    except ValueError:
        return await message.reply_text("❌ <b>User ID and days must be numeric.</b>")

    tier = "pro" if message.command[0] == "add_premium_pro" else "pro_gold"
    expires_at = await db.set_premium(user_id, tier, days)
    expiry_text = expires_at.astimezone(IST).strftime("%d %b %Y, %I:%M %p IST")
    await message.reply_text(f"✅ <b>{tier.upper()} activated for</b> <code>{user_id}</code> <b>till</b> <code>{expiry_text}</code>.")


@Client.on_message(filters.command(["removeverifytime"]) & filters.private)
async def remove_verify_time(client, message):
    if message.from_user.id != ADMINS:
        return await message.reply_text("❌ <b>Only admin can use this command.</b>")
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b> <code>/removeverifytime userid</code>")
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ <b>User ID must be numeric.</b>")

    await db.reset_verify_time(user_id)
    await message.reply_text(f"✅ <b>Verification reset for</b> <code>{user_id}</code>.")


@Client.on_message(filters.command(["remove_premium"]) & filters.private)
async def remove_premium(client, message):
    if message.from_user.id != ADMINS:
        return await message.reply_text("❌ <b>Only admin can use this command.</b>")
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b> <code>/remove_premium userid</code>")
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ <b>User ID must be numeric.</b>")
    await db.remove_premium(user_id)
    await message.reply_text(f"✅ <b>Premium removed for</b> <code>{user_id}</code>.")


@Client.on_message(filters.command(["ban"]) & filters.private)
async def ban_user(client, message):
    if message.from_user.id != ADMINS:
        return await message.reply_text("❌ <b>Only admin can use this command.</b>")
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b> <code>/ban userid</code>")
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ <b>User ID must be numeric.</b>")
    await db.set_ban_status(user_id, True)
    await message.reply_text(f"✅ <b>User banned:</b> <code>{user_id}</code>")


@Client.on_message(filters.command(["unban"]) & filters.private)
async def unban_user(client, message):
    if message.from_user.id != ADMINS:
        return await message.reply_text("❌ <b>Only admin can use this command.</b>")
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b> <code>/unban userid</code>")
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ <b>User ID must be numeric.</b>")
    await db.set_ban_status(user_id, False)
    await message.reply_text(f"✅ <b>User unbanned:</b> <code>{user_id}</code>")


@Client.on_callback_query(filters.regex("^premium_btn$"))
async def premium_btn(client, query):
    if await db.is_banned(query.from_user.id):
        await query.answer("You are banned from using this bot.", show_alert=True)
        return
    current_text = (query.message.text or query.message.caption or "").strip()
    if current_text == PREMIUM_OVERVIEW_TEXT.strip():
        await query.answer()
        return

    await query.message.edit_text(
        PREMIUM_OVERVIEW_TEXT,
        reply_markup=premium_keyboard(),
        disable_web_page_preview=True
    )
    await query.answer()


@Client.on_callback_query(filters.regex("^plan_pro$"))
async def pro_btn(client, query):
    if await db.is_banned(query.from_user.id):
        await query.answer("You are banned from using this bot.", show_alert=True)
        return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(PREMIUM_CONTACT_BUTTON_TEXT, url=PREMIUM_CONTACT_URL)],
        [InlineKeyboardButton("⬅️ Back To Plans", callback_data="premium_btn")]
    ])
    await client.send_photo(query.message.chat.id, PRO_PLAN_QR_IMAGE, caption=f"<b>{PRO_PLAN_NAME}</b>\n\n{PRO_PLAN_DETAILS}", reply_markup=kb)
    await query.answer()


@Client.on_callback_query(filters.regex("^plan_pro_gold$"))
async def gold_btn(client, query):
    if await db.is_banned(query.from_user.id):
        await query.answer("You are banned from using this bot.", show_alert=True)
        return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(PREMIUM_CONTACT_BUTTON_TEXT, url=PREMIUM_CONTACT_URL)],
        [InlineKeyboardButton("⬅️ Back To Plans", callback_data="premium_btn")]
    ])
    await client.send_photo(query.message.chat.id, PRO_GOLD_PLAN_QR_IMAGE, caption=f"<b>{PRO_GOLD_PLAN_NAME}</b>\n\n{PRO_GOLD_PLAN_DETAILS}", reply_markup=kb)
    await query.answer()
