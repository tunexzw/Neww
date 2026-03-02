# ---------------------------------------------------
# File Name: Start.py
# Author: NeonAnurag
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# YouTube: https://youtube.com/@MyselfNeon
# Created: 2025-10-21
# Last Modified: 2025-10-22
# Version: Latest
# License: MIT License
# ---------------------------------------------------

import os
import asyncio
import random
from datetime import datetime, timezone
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, MessageEntity
from config import (
    API_ID, API_HASH, ERROR_MESSAGE, VERIFY_TUTORIAL, START_PIC, DUMP_CHANNEL,
    FREE_SAVE_COOLDOWN_SECONDS, PRO_DAILY_BATCH_LIMIT, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL_URL,
    FORCE_SUB_PIC, BYPASS_ALERT_PIC, VERIFY_PIC, AUTO_DELETE_SECONDS
)
from database.db import db
from MyselfNeon.strings import HELP_TXT
from MyselfNeon.verify import check_token, process_verification_success, check_verification, get_token

class batch_temp(object):
    IS_BATCH = {}


async def get_user_tier(user_id: int):
    tier, _ = await db.get_active_tier(user_id)
    return tier


def is_batch_request(from_id: int, to_id: int):
    return to_id > from_id


async def enforce_free_cooldown(message: Message):
    last_save_at = await db.get_last_save_at(message.from_user.id)
    if not last_save_at:
        return True, None

    now_utc = datetime.now(timezone.utc)
    if last_save_at.tzinfo is None:
        last_save_at = last_save_at.replace(tzinfo=timezone.utc)

    elapsed = (now_utc - last_save_at).total_seconds()
    if elapsed >= FREE_SAVE_COOLDOWN_SECONDS:
        return True, None

    remaining = int(FREE_SAVE_COOLDOWN_SECONDS - elapsed)
    return False, remaining


async def check_ban_and_reply(message: Message):
    if await db.is_banned(message.from_user.id):
        await message.reply_text(
            "🚫 <b>You are blocked due to suspicious activity.</b>\n\n"
            "<b>You cannot use this bot. Please contact admin for unban.</b>"
        )
        return True
    return False

async def is_user_subscribed(client: Client, user_id: int):
    if not FORCE_SUB_CHANNEL:
        return True

    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        status = str(getattr(member, "status", "")).lower()
        allowed = {
            "member", "administrator", "creator", "restricted",
            "chatmemberstatus.member", "chatmemberstatus.administrator",
            "chatmemberstatus.owner", "chatmemberstatus.restricted"
        }
        return status in allowed
    except UserNotParticipant:
        return False
    except Exception:
        return False


async def check_force_sub(client: Client, message: Message):
    if await is_user_subscribed(client, message.from_user.id):
        return True

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=FORCE_SUB_CHANNEL_URL)],
        [InlineKeyboardButton("✅ Joined", callback_data="force_sub_check")]
    ])
    if FORCE_SUB_PIC:
        await message.reply_photo(
            FORCE_SUB_PIC,
            caption="<b>🔒 You must join our updates channel before using this bot.</b>",
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            "<b>🔒 You must join our updates channel before using this bot.</b>",
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    return False

async def auto_delete_later(client: Client, chat_id: int, message_ids):
    if not AUTO_DELETE_SECONDS or AUTO_DELETE_SECONDS <= 0:
        return
    if not isinstance(message_ids, list):
        message_ids = [message_ids]
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    try:
        await client.delete_messages(chat_id, message_ids)
    except Exception:
        pass


def schedule_auto_delete(client: Client, sent_msg: Message):
    if sent_msg and AUTO_DELETE_SECONDS and AUTO_DELETE_SECONDS > 0:
        asyncio.create_task(auto_delete_later(client, sent_msg.chat.id, sent_msg.id))


# --- Supported Telegram Reactions ---
REACTIONS = [
    "🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩",
    "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡",
    "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"
]

# --- Download status ---
async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"Downloaded: {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# --- Upload status ---
async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"Uploaded: {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# --- Progress writer ---
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# --- Helper: Generate Footer for Dump ---
def get_formatted_footer(message, msg_link, caption, original_entities):
    # 1. Format User Info
    if message.from_user.username:
        user_line = f"User - @{message.from_user.username}"
    else:
        user_line = f"User - {message.from_user.first_name} ({message.from_user.id})"

    # 2. Construct Footer Text
    footer_text = f"{user_line}\nLink - Click Here"
    
    # 3. Combine with Caption
    # If caption exists, add newlines. If not, just footer.
    full_text = f"{caption}\n\n{footer_text}" if caption else footer_text
    
    # 4. Calculate Entities
    entities = list(original_entities) if original_entities else []
    
    # Offset starts at end of original caption + 2 newlines (if caption existed)
    footer_offset = len(caption) + 2 if caption else 0
    
    # --- Add Entities ---
    # Blockquote
    entities.append(MessageEntity(type=enums.MessageEntityType.BLOCKQUOTE, offset=footer_offset, length=len(footer_text)))
    # Bold
    entities.append(MessageEntity(type=enums.MessageEntityType.BOLD, offset=footer_offset, length=len(footer_text)))
    # Italic
    entities.append(MessageEntity(type=enums.MessageEntityType.ITALIC, offset=footer_offset, length=len(footer_text)))
    
    # Link (Text Link for "Click Here")
    # "Link - " is 7 chars. Click Here starts at offset + len(user_line) + 1 + 7
    link_start = footer_offset + len(user_line) + 1 + 7
    entities.append(MessageEntity(type=enums.MessageEntityType.TEXT_LINK, offset=link_start, length=10, url=msg_link))
    
    return full_text, entities

# --- Start command ---
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if await check_ban_and_reply(message):
        return

    if not await check_force_sub(client, message):
        return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(
            message.from_user.id, 
            message.from_user.first_name, 
            message.from_user.username
        )

    # --- Verification Check For Deep Links ---
    if len(message.command) > 1:
        data = message.command[1]
        if data.split("-")[0] == "verify":
            try:
                _, user_id, token = data.split("-")
                user_id = int(user_id)
            except:
                return await message.reply("❌ Invalid Verification Link.")

            if message.from_user.id != user_id:
                return await message.reply("❌ This link is not for you!")

            if await check_token(user_id, token):
                result = await process_verification_success(client, user_id, token)
                if result.get("banned_now"):
                    return await message.reply("🚫 <b>Repeated bypass detected. You are now banned from this bot.</b>")

                if result.get("bypass_detected"):
                    if BYPASS_ALERT_PIC:
                        return await message.reply_photo(
                            BYPASS_ALERT_PIC,
                            caption="⚠️ <b>Verification bypass detected.</b>\n\n<b>Please verify again to continue using the bot.</b>"
                        )
                    return await message.reply("⚠️ <b>Verification bypass detected.</b>\n\n<b>Please verify again to continue using the bot.</b>")

                return await message.reply("<b><i>✅ Verification Successful!</i></b>\n\n<b><i>You can now Use the Bot for 4 Hours.</i></b>")
            else:
                return await message.reply("<b><i>❌ Invalid or Expired Token!</i></b>\n\n<b><i>Use /verify to get a new one.</b></i>")

    buttons = [
        [
            InlineKeyboardButton("Hᴏᴡ Tᴏ Usᴇ Mᴇ 🤔", callback_data="help_btn"),
            InlineKeyboardButton("💎 Premium Plans", callback_data="premium_btn")
        ],
        [
            InlineKeyboardButton('Uᴘᴅᴀᴛᴇ 🔥', url='https://t.me/NeonFiles'),
            InlineKeyboardButton('Aʙᴏᴜᴛ 😎', callback_data="about_btn")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    start_text = (
        f"<blockquote>**__Yoo !! {message.from_user.mention}__ 😇**</blockquote>\n"
        "<blockquote>**__I’m Save Restricted Content Bot. I Can Help You Unlock And Save Restricted Posts From Telegram By Their Links.__**\n\n"
        "**__🔑 Please /login First — This Is Required For Downloading Content.__**</blockquote>\n"
        "<blockquote>**__Try new @SaveRestrictions_oBot__**</blockquote>"
    )

    if START_PIC:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=START_PIC,
            caption=start_text,
            reply_markup=reply_markup,
            reply_to_message_id=message.id
        )
    else:
        await client.send_message(
            chat_id=message.chat.id,
            text=start_text,
            reply_markup=reply_markup,
            reply_to_message_id=message.id
        )

    try:
        await message.react(
            emoji=random.choice(REACTIONS),
            big=True
        )
    except Exception as e:
        print(f"Reaction failed: {e}")

# --- Help command ---
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}"
    )

# --- Cancel command ---
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id,
        text="❌ Batch Successfully Cancelled.",
        quote=True
    )

# --- Handle incoming messages ---
@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "cancel", "verify", "premium", "my_plan", "login", "logout", "login_session", "add_premium_pro", "add_premium_gold", "remove_premium", "removeverifytime", "ban", "unban"]))
async def save(client: Client, message: Message):
    if await check_ban_and_reply(message):
        return

    if not await check_verification(message.from_user.id):
        btn = [[
            InlineKeyboardButton("Verify Now", callback_data="verify_query"),
            InlineKeyboardButton("💎 Premium Plans", callback_data="premium_btn")
        ]]
        return await message.reply_text(
            "❌ <b><i>You are not Verified!</i></b>\n\n<i><b>Please Verify your Account to Download Files.</b></i>",
            reply_markup=InlineKeyboardMarkup(btn)
        )

    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text(
                "One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel"
            )

        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        tier = await get_user_tier(message.from_user.id)
        destination_chat_id = await db.get_destination_chat(message.from_user.id) if tier == "pro_gold" else None
        requested_count = (toID - fromID) + 1
        is_batch = is_batch_request(fromID, toID)

        if tier == "free" and is_batch:
            return await message.reply_text("❌ Free users cannot use batch links. Upgrade to PRO/PRO GOLD.")

        if tier == "free":
            ok, remaining = await enforce_free_cooldown(message)
            if not ok:
                return await message.reply_text(
                    f"⏳ Free cooldown active. Please wait {remaining} seconds before saving next message."
                )

        if tier == "pro" and is_batch:
            used_today = await db.get_batch_daily_count(message.from_user.id)
            if used_today + requested_count > PRO_DAILY_BATCH_LIMIT:
                left = max(0, PRO_DAILY_BATCH_LIMIT - used_today)
                return await message.reply_text(
                    f"⚠️ PRO batch daily limit reached. Remaining today: {left}/{PRO_DAILY_BATCH_LIMIT}."
                )

        batch_temp.IS_BATCH[message.from_user.id] = False

        for msgid in range(fromID, toID + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**__For Downloading Restricted Content You Have To /login First.__**")
                batch_temp.IS_BATCH[message.from_user.id] = True
                return

            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
            except:
                batch_temp.IS_BATCH[message.from_user.id] = True
                return await message.reply("**__Your Login Session Expired. So /logout First Then Login Again By - /login__**")

            # ------------------------------------------------------------------
            # SEND INITIAL PROCESSING MESSAGE
            # ------------------------------------------------------------------
            smsg = await message.reply_text("**__Processing ...__**", quote=True)

            # --- PRIVATE CHANNELS ---
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid, status_msg=smsg, destination_chat_id=destination_chat_id)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # --- PRIVATE BOTS ---
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid, status_msg=smsg, destination_chat_id=destination_chat_id)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # --- PUBLIC CHANNELS (FAST COPY WITH DETECTED MSG) ---
            else:
                username = datas[3]
                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    await client.send_message(message.chat.id, "**__The username is not occupied by anyone.__**",
                                              reply_to_message_id=message.id)
                    return
                
                try:
                    await smsg.edit("**__Downloading 🚀__**")
                    user_copy = await client.copy_message(message.chat.id, msg.chat.id, msg.id)
                    await smsg.edit("**__Uploading 📤__**")

                    if destination_chat_id:
                        await client.copy_message(destination_chat_id, message.chat.id, user_copy.id)

                    schedule_auto_delete(client, user_copy)

                    # 3. Send to Dump (WITH FOOTER)
                    if DUMP_CHANNEL:
                        msg_link = f"https://t.me/{username}/{msgid}"
                        
                        if msg.text:
                            # For Text: Construct new message with footer
                            full_text, text_entities = get_formatted_footer(message, msg_link, msg.text, msg.entities)
                            await client.send_message(DUMP_CHANNEL, full_text, entities=text_entities)
                        else:
                            # For Media: Copy with new caption
                            original_caption = msg.caption if msg.caption else ""
                            full_caption, full_entities = get_formatted_footer(message, msg_link, original_caption, msg.caption_entities)
                            
                            await client.copy_message(
                                DUMP_CHANNEL, 
                                msg.chat.id, 
                                msg.id, 
                                caption=full_caption, 
                                caption_entities=full_entities
                            )

                    # 4. Delete Status Message
                    await smsg.delete()

                except Exception as e:
                    # If Copy Fails (Restricted Public), Fallback to Downloader
                    try:
                        await handle_private(client, acc, message, username, msgid, status_msg=smsg, destination_chat_id=destination_chat_id)
                    except Exception as e:
                        if ERROR_MESSAGE:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            await asyncio.sleep(3)

        if tier == "pro" and is_batch:
            await db.increment_batch_daily_count(message.from_user.id, requested_count)

        if tier == "free":
            await db.set_last_save_at(message.from_user.id)

        batch_temp.IS_BATCH[message.from_user.id] = True
        
# --- Handle private content ---
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int, status_msg: Message = None, destination_chat_id: int = None):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty:
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    if isinstance(chatid, int):
        c_id_str = str(chatid)
        clean_id = c_id_str[4:] if c_id_str.startswith("-100") else c_id_str
        msg_link = f"https://t.me/c/{clean_id}/{msgid}"
    else:
        msg_link = f"https://t.me/{chatid}/{msgid}"

    original_caption = msg.caption if msg.caption else ""
    original_entities = msg.caption_entities if msg.caption_entities else []
    full_dump_text, dump_entities = get_formatted_footer(message, msg_link, original_caption, original_entities)

    if status_msg:
        try:
            smsg = await status_msg.edit('**__Downloading 🚀__**')
        except Exception:
            smsg = await client.send_message(chat, '**__Downloading 🚀__**', reply_to_message_id=message.id)
    else:
        smsg = await client.send_message(chat, '**__Downloading 🚀__**', reply_to_message_id=message.id)

    user_sent = None

    if msg_type == "Text":
        try:
            await smsg.edit('**__Uploading 📤__**')
            user_sent = await client.send_message(chat, msg.text, entities=msg.entities)
            if destination_chat_id:
                await client.copy_message(destination_chat_id, chat, user_sent.id)
            schedule_auto_delete(client, user_sent)

            if DUMP_CHANNEL:
                full_text_dump, full_text_entities = get_formatted_footer(message, msg_link, msg.text, msg.entities)
                await client.send_message(DUMP_CHANNEL, full_text_dump, entities=full_text_entities)
            await smsg.delete()
            return
        except Exception as e:
            if ERROR_MESSAGE:
                err = await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                schedule_auto_delete(client, err)
            await smsg.delete()
            return

    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        if os.path.exists(f'{message.id}downstatus.txt'):
            os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE:
            err = await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            schedule_auto_delete(client, err)
        return await smsg.delete()

    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))
    caption = msg.caption if msg.caption else ""

    try:
        if msg_type == "Document":
            try:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except Exception:
                ph_path = None
            user_sent = await client.send_document(chat, file, thumb=ph_path, caption=caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
            if DUMP_CHANNEL:
                await client.send_document(DUMP_CHANNEL, file, thumb=ph_path, caption=full_dump_text, caption_entities=dump_entities)
            if ph_path:
                os.remove(ph_path)

        elif msg_type == "Video":
            try:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            except Exception:
                ph_path = None
            user_sent = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
            if DUMP_CHANNEL:
                await client.send_video(DUMP_CHANNEL, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=full_dump_text, caption_entities=dump_entities)
            if ph_path:
                os.remove(ph_path)

        elif msg_type == "Animation":
            user_sent = await client.send_animation(chat, file, caption=caption, caption_entities=msg.caption_entities)
            if DUMP_CHANNEL:
                await client.send_animation(DUMP_CHANNEL, file, caption=full_dump_text, caption_entities=dump_entities)

        elif msg_type == "Sticker":
            user_sent = await client.send_sticker(chat, file)

        elif msg_type == "Voice":
            user_sent = await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
            if DUMP_CHANNEL:
                await client.send_voice(DUMP_CHANNEL, file, caption=full_dump_text, caption_entities=dump_entities)

        elif msg_type == "Audio":
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            except Exception:
                ph_path = None
            user_sent = await client.send_audio(chat, file, thumb=ph_path, caption=caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
            if DUMP_CHANNEL:
                await client.send_audio(DUMP_CHANNEL, file, thumb=ph_path, caption=full_dump_text, caption_entities=dump_entities)
            if ph_path:
                os.remove(ph_path)

        elif msg_type == "Photo":
            user_sent = await client.send_photo(chat, file, caption=caption, caption_entities=msg.caption_entities)
            if DUMP_CHANNEL:
                await client.send_photo(DUMP_CHANNEL, file, caption=full_dump_text, caption_entities=dump_entities)

        if user_sent and destination_chat_id:
            await client.copy_message(destination_chat_id, chat, user_sent.id)

        if user_sent:
            schedule_auto_delete(client, user_sent)

    except Exception as e:
        if ERROR_MESSAGE:
            err = await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            schedule_auto_delete(client, err)

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    if 'file' in locals() and os.path.exists(file):
        os.remove(file)

    await client.delete_messages(chat, [smsg.id])

# --- Get message type ---
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass
    try:
        msg.video.file_id
        return "Video"
    except:
        pass
    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass
    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass
    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass
    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass
    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass
    try:
        msg.text
        return "Text"
    except:
        pass

# --- Inline button callback ---
@Client.on_callback_query()
async def button_callbacks(client: Client, callback_query):
    data = callback_query.data
    message = callback_query.message

    # --- NEW VERIFY BUTTON HANDLE ---
    if data == "verify_query":
        if await db.is_banned(callback_query.from_user.id):
            await callback_query.answer("You are banned from using this bot.", show_alert=True)
            return

        # Acknowledge the callback immediately to stop the spinning
        await callback_query.answer("Generating link...", show_alert=False)
        
        bot_info = await client.get_me()
        start_link = f"https://t.me/{bot_info.username}?start="
        
        try:
            # Generate the token and short link
            verify_url = await get_token(client, callback_query.from_user.id, start_link)
            
            buttons = [
                [InlineKeyboardButton("🔗 Click Here To Verify", url=verify_url)],
                [InlineKeyboardButton("❓ How To Verify", url=VERIFY_TUTORIAL)],
                [InlineKeyboardButton("💎 Premium Plans", callback_data="premium_btn")]
            ]
            
            await client.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.id,
                text="<b><i>🔐 Verification Required !</i></b>\n\n"
                     "<i><b>To continue using this Bot, you must Verify your Account.</i></b>\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"Error generating link: {e}")

    elif data == "force_sub_check":
        if not FORCE_SUB_CHANNEL:
            await callback_query.answer("Force subscription is disabled.", show_alert=True)
            return

        if await is_user_subscribed(client, callback_query.from_user.id):
            await callback_query.answer("✅ Subscription verified.", show_alert=False)
            await callback_query.message.delete()
            return

        await callback_query.answer("❌ Please join the channel first.", show_alert=True)

    # Help button  
    elif data == "help_btn":
        help_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Cʟᴏsᴇ ❌", callback_data="close_btn"),
                InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="start_btn")
            ]
        ])
        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=HELP_TXT,
            reply_markup=help_buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await callback_query.answer()

    # About button
    elif data == "about_btn":
        me = await client.get_me()
        about_text = (
            "<b><blockquote>‣ 📝 𝐌𝐘 𝐃𝐄𝐓𝐀𝐈𝐋𝐒</blockquote>\n"
            "<blockquote><i>• Mʏ Nᴀᴍᴇ : <a href='https://t.me/SaveRestriction_oBot'>Save Restrictions</a>\n"
            "• Mʏ Bᴇsᴛ Fʀɪᴇɴᴅ : <a href='tg://settings'>Tʜɪs Sᴡᴇᴇᴛɪᴇ ❤️</a>\n"
            "• Dᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/MyselfNeon'>@MʏsᴇʟғNᴇᴏɴ</a>\n"
            "• Lɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ</a>\n"
            "• Lᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>Pʏᴛʜᴏɴ 𝟹</a>\n"
            "• DᴀᴛᴀBᴀsᴇ : <a href='https://www.mongodb.com/'>Mᴏɴɢᴏ DB</a>\n"
            "• Bᴏᴛ Sᴇʀᴠᴇʀ : <a href='https://heroku.com'>Hᴇʀᴏᴋᴜ</a>\n"
            "• Bᴜɪʟᴅ Sᴛᴀᴛᴜs : ᴠ𝟸.𝟽 [Sᴛᴀʙʟᴇ]</i></b></blockquote>"
        )

        about_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ 🔊", url="https://t.me/+o1s-8MppL2syYTI9"),
                InlineKeyboardButton("Sᴏᴜʀᴄᴇ Cᴏᴅᴇ 💡", url="https://myselfneon.github.io/neon/")
            ],
            [
                InlineKeyboardButton("Cʟᴏsᴇ ❌", callback_data="close_btn"),
                InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="start_btn")
            ]
        ])

        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=about_text,
            reply_markup=about_buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await callback_query.answer()

    # --- Home / Start button ---
    elif data == "start_btn":
        start_buttons = InlineKeyboardMarkup([
            [
            InlineKeyboardButton("Hᴏᴡ Tᴏ Usᴇ Mᴇ 🤔", callback_data="help_btn"),
            InlineKeyboardButton("💎 Premium Plans", callback_data="premium_btn")
        ],
            [
                InlineKeyboardButton("Uᴘᴅᴀᴛᴇ 🔥", url="https://t.me/NeonFiles"),
                InlineKeyboardButton("Aʙᴏᴜᴛ 😎", callback_data="about_btn")
            ]
        ])
        await client.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=(
                f"<blockquote>**__Yoo !! {callback_query.from_user.mention}__ 👋**</blockquote>\n"
                "<blockquote>**__I’m Save Restricted Content Bot. I Can Help You Unlock And Save Restricted Posts From Telegram By Their Links.__**\n\n"
                "**__🔑 Please /login First — This Is Required For Downloading Content.__**</blockquote>\n"
                "<blockquote>**__Try new @SaveRestrictions_oBot__**</blockquote>"
            ),
            reply_markup=start_buttons
        )
        await callback_query.answer()

    # --- Close button ---
    elif data == "close_btn":
        await client.delete_messages(message.chat.id, [message.id])
        await callback_query.answer()


# Don't remove Credits
# Developer Telegram @MyselfNeon
# Update channel - @NeonFiles
