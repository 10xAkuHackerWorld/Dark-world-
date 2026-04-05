import logging
import asyncio
import os
import time
from threading import Thread
from flask import Flask
from telegram import Update, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# --- FLASK WEB SERVER ---
app_web = Flask(__name__)
import logging as flask_logging
flask_logging.getLogger('werkzeug').setLevel(flask_logging.ERROR)

@app_web.route('/')
def home():
    return "Bot is alive and running 24/7 on Render!"

# 🔹 Aapka Bot Token aur Owner Username
TOKEN = "8603465694:AAE_lfAe6SbOEbC7hbzDkAfwV_JhaPqFhro"
SUPPORT_USERNAME = "Dark_a09" # Bina '@' ke URL ke liye

# 🔹 Bad words load karna
try:
    with open("bad_words.txt", "r", encoding="utf-8") as f:
        BAD_WORDS = [line.strip().lower() for line in f.readlines() if line.strip()]
except FileNotFoundError:
    BAD_WORDS = ["mc", "bc", "madarchod", "behenchod"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

background_tasks = set()
user_warnings = {}  
USER_CACHE = {}     

# --- ⏱️ TIMERS ---
async def delete_after_time(bot, chat_id, message_id, sleep_time):
    await asyncio.sleep(sleep_time)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# --- ⬛ STYLISH MESSAGE SENDER (Clean Theme) ---
async def send_stylish_message(bot, chat_id, text, auto_delete=True):
    if auto_delete:
        formatted_message = f"{text}\n\n⏳ <i>(Auto-delete in 1 minute)</i>"
    else:
        formatted_message = text
        
    try:
        msg = await bot.send_message(chat_id=chat_id, text=formatted_message, parse_mode="HTML")
        if auto_delete:
            task = asyncio.create_task(delete_after_time(bot, chat_id, msg.message_id, 60))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
    except Exception as e:
        logging.error(f"Send Error: {e}")

# --- 👑 STATUS CHECKER ---
async def get_user_status(chat_id, user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status 
    except Exception:
        return 'member'

# --- 1️⃣ START & RULES COMMAND (DM KE LIYE) ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.message.chat.type
    
    # Agar user DM me 'Rules' button click karke aata hai
    if chat_type == 'private':
        rules_text = f"""<b>📋 DARK WORLD RULES 📋</b>

<blockquote>1. 🛑 <b>No Abusive Language:</b> 3 Warnings ke baad 24 Hours ke liye MUTE.
2. 🔗 <b>No Links:</b> Group me kisi bhi tarah ki external link bhejna sakt mana hai.
3. ✏️ <b>No Editing:</b> Message send hone ke baad usko edit karna allowed nahi hai.
4. 🧹 <b>Auto-Clean:</b> Group ka har ek message 5 ghante me apne aap delete ho jayega.
5. 🛡️ <b>Admin Powers:</b> Ye rules sirf normal members ke liye hain. Group owner aur admins par rules lagu nahi hote.</blockquote>

<i>Follow the rules and enjoy your time!</i> 🖤"""
        await update.message.reply_text(rules_text, parse_mode="HTML")
        return

    # Agar group me normal /start lagaya
    mention = update.effective_user.first_name
    start_text = f"<b>HELLO {mention}! 👋</b>\n\nMain is group ka Manager Bot hoon. Main rules maintain rakhta hoon."
    await send_stylish_message(context.bot, update.message.chat.id, start_text, auto_delete=True)

# --- 2️⃣ PING COMMAND ---
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("<i>Pinging...</i>", parse_mode="HTML")
    end_time = time.time()
    
    ping_time = round((end_time - start_time) * 1000)
    ping_text = f"""<blockquote>🏓 <b>PONG!</b>

⚡ Latency: <b>{ping_time}ms</b>
🤖 Status: <b>Alive & Active</b>

— Admin: @{SUPPORT_USERNAME}</blockquote>"""
    
    try:
        await msg.delete()
    except:
        pass
    await send_stylish_message(context.bot, update.message.chat.id, ping_text, auto_delete=True)

# --- 3️⃣ ID COMMAND ---
async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.effective_user
    chat_id = update.message.chat.id
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user

    user_id = target_user.id
    first_name = target_user.first_name if target_user.first_name else "N/A"
    last_name = target_user.last_name if target_user.last_name else "N/A"
    username = f"@{target_user.username}" if target_user.username else "N/A"
    
    info_text = f"""<blockquote>🕵️‍♂️ <b>USER INFORMATION</b> 🕵️‍♂️

👤 <b>First Name:</b> {first_name}
👤 <b>Last Name:</b> {last_name}
🔗 <b>Username:</b> {username}
🆔 <b>User ID:</b> <code>{user_id}</code>
💬 <b>Chat ID:</b> <code>{chat_id}</code>

<i>Note: Phone numbers are hidden by Telegram Privacy Policy.</i></blockquote>"""
    await send_stylish_message(context.bot, chat_id, info_text, auto_delete=True)

# --- 4️⃣ UNMUTE COMMAND ---
async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_id = update.effective_user.id
    
    status = await get_user_status(chat_id, user_id, context.bot)
    if status != 'creator':
        await send_stylish_message(context.bot, chat_id, "<blockquote>🛑 <b>ACCESS DENIED</b>\nYe command sirf Group Owner use kar sakta hai!</blockquote>", auto_delete=True)
        return

    target_user_id = None
    target_username = None

    if update.message.reply_to_message:
        target_user_id = update.message.reply_to_message.from_user.id
        target_username = update.message.reply_to_message.from_user.username
    elif context.args:
        uname = context.args[0].replace("@", "").lower()
        target_user_id = USER_CACHE.get(uname)
        target_username = uname

    if not target_user_id:
        await send_stylish_message(context.bot, chat_id, "<blockquote>⚠️ <b>ERROR</b>\nUser data nahi mila! Kripya message par reply karke /unmute try karein.</blockquote>", auto_delete=True)
        return

    try:
        await context.bot.restrict_chat_member(
            chat_id, target_user_id,
            permissions=ChatPermissions(
                can_send_messages=True, can_send_audios=True, can_send_documents=True,
                can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
                can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        user_warnings[(chat_id, target_user_id)] = 0 
        display_name = f"@{target_username}" if target_username else str(target_user_id)
        await send_stylish_message(context.bot, chat_id, f"<blockquote>✅ <b>TARGET UNMUTED</b>\n\n👤 User: {display_name}\nYe user ab wapas messages bhej sakta hai.</blockquote>", auto_delete=True)
    except Exception as e:
        logging.error(f"Unmute Error: {e}")

# --- 5️⃣ VIP WELCOME MESSAGE HANDLER (NEW THEME & IMAGE FIX) ---
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    bot_username = context.bot.username
    
    # 2 Sec me system message delete
    task = asyncio.create_task(delete_after_time(context.bot, chat_id, update.message.message_id, 2))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    # 🔹 Naya Function: Group ki details aur image fully fetch karna
    try:
        full_chat = await context.bot.get_chat(chat_id)
    except Exception:
        full_chat = update.message.chat

    chat_title = full_chat.title if full_chat.title else "THE GROUP"
    
    # Group Owner ka naam dhoondhna
    group_owner_name = "ADMIN"
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.status == 'creator':
                group_owner_name = admin.user.first_name.upper()
                break
    except Exception:
        pass

    for member in update.message.new_chat_members:
        if member.id == context.bot.id: 
            continue
            
        username_display = f"{member.username}" if member.username else "N/A"
        first_name = member.first_name if member.first_name else "Unknown"
        
        # New Aesthetic Message Format (Exact match)
        welcome_text = f"""<b>🪩 WELCOME TO {chat_title.upper()}</b>

<blockquote>⭐️ NAME - {first_name}
❀ USERNAME - {username_display}
✨ USER ID - <code>{member.id}</code></blockquote>

WELCOME TO A NEW WORLD OF FUN, JOY AND NON-sTOP ENTERTAINMENT, WHERE EVERY MOMENT Is FULL OF HAPPINEss.>

<blockquote>🔮 OWNER - {group_owner_name}</blockquote>"""

        # Inline Buttons Setup
        keyboard = [
            [InlineKeyboardButton("『 R U L E S 』", url=f"https://t.me/{bot_username}?start=rules")],
            [InlineKeyboardButton("『 S U P P O R T 』", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 🔹 Naya Image Sender: Agar group ki photo fetch hui toh bhejo
        photo_sent = False
        if full_chat.photo:
            try:
                photo_file_id = full_chat.photo.big_file_id
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file_id, caption=welcome_text, parse_mode="HTML", reply_markup=reply_markup)
                photo_sent = True
            except Exception as e:
                logging.error(f"Image fetch error: {e}")
                
        # Agar koi image nahi mili, toh sirf text bhej do
        if not photo_sent:
            await context.bot.send_message(chat_id=chat_id, text=welcome_text, parse_mode="HTML", reply_markup=reply_markup)

# --- 6️⃣ OTHER SYSTEM NOTIFICATIONS ---
async def system_notification_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        task = asyncio.create_task(delete_after_time(context.bot, update.message.chat.id, update.message.message_id, 2))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

# --- 7️⃣ EDITED MESSAGE HANDLER ---
async def edited_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.edited_message.from_user
    chat_id = update.edited_message.chat.id
    
    status = await get_user_status(chat_id, user.id, context.bot)
    if status in ['creator', 'administrator']:
        return

    try: 
        await update.edited_message.delete()
    except Exception: 
        pass
        
    username_display = f"@{user.username}" if user.username else user.first_name
    edit_text = f"<blockquote>🛑 <b>EDIT DETECTED</b>\n\n👤 User: {username_display}\n\nGroup me message edit karna allowed nahi hai.</blockquote>"
    await send_stylish_message(context.bot, chat_id, edit_text, auto_delete=True)

# --- 8️⃣ ALL MESSAGES PROCESSOR (CLEAN THEME) ---
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    user = update.message.from_user

    if user.username:
        USER_CACHE[user.username.lower()] = user.id

    task_5h = asyncio.create_task(delete_after_time(context.bot, chat_id, message_id, 18000))
    background_tasks.add(task_5h)
    task_5h.add_done_callback(background_tasks.discard)

    text = update.message.text.lower() if update.message.text else ""
    if not text:
        return 
        
    username_display = f"@{user.username}" if user.username else user.first_name
    status = await get_user_status(chat_id, user.id, context.bot)

    has_bad_word = any(word in text.replace('.',' ').split() for word in BAD_WORDS)
    if has_bad_word:
        if status == 'creator':
            return 
            
        try: 
            await update.message.delete()
        except Exception: 
            pass
            
        max_warnings = 5 if status == 'administrator' else 3
        user_key = (chat_id, user.id)
        current_warnings = user_warnings.get(user_key, 0) + 1
        user_warnings[user_key] = current_warnings

        if current_warnings >= max_warnings:
            try:
                mute_time = int(time.time()) + 86400 
                await context.bot.restrict_chat_member(chat_id, user.id, permissions=ChatPermissions(can_send_messages=False), until_date=mute_time)
                mute_text = f"<blockquote>🛑 <b>BAN APPLIED</b>\n\n👤 User: {username_display}\n🚫 Reason: {max_warnings} Warnings Completed.\n\nAapko 24 ghante ke liye MUTE kar diya gaya hai.</blockquote>"
                await send_stylish_message(context.bot, chat_id, mute_text, auto_delete=True)
                user_warnings[user_key] = 0 
            except Exception as e:
                if "administrators" in str(e).lower():
                    admin_err_text = f"<blockquote>⚠️ <b>ADMIN ERROR</b>\n\n👤 User: {username_display}\n\nGroup Admin hone ki wajah se bot inhe mute nahi kar sakta. Owner ko manually karna hoga.</blockquote>"
                    await send_stylish_message(context.bot, chat_id, admin_err_text, auto_delete=True)
                    user_warnings[user_key] = 0
        else:
            warn_text = f"<blockquote>⚠️ <b>WARNING ({current_warnings}/{max_warnings})</b>\n\n👤 User: {username_display}\n🚫 Reason: Abusive Language.\n\nApni bhasha sudharein warna Mute kar diye jaoge.</blockquote>"
            await send_stylish_message(context.bot, chat_id, warn_text, auto_delete=True)
        return 

    if status not in ['creator', 'administrator']:
        has_link = "http://" in text or "https://" in text or "t.me/" in text or ".com" in text
        if has_link:
            try: 
                await update.message.delete()
            except Exception: 
                pass
            link_text = f"<blockquote>🛑 <b>LINK DETECTED</b>\n\n👤 User: {username_display}\n\nGroup me kisi bhi tarah ki Link bhejna mana hai.</blockquote>"
            await send_stylish_message(context.bot, chat_id, link_text, auto_delete=True)

# --- BOT KO BACKGROUND ME CHALANE WALA FUNCTION ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("unmute", unmute_cmd)) 
    app.add_handler(CommandHandler("ping", ping_cmd)) 
    app.add_handler(CommandHandler("id", id_cmd)) 
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.ALL & ~filters.StatusUpdate.NEW_CHAT_MEMBERS, system_notification_handler))
    
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited_message_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.UpdateType.EDITED_MESSAGE, process_message))

    print("✅ Telegram Bot running successfully in background!", flush=True)
    app.run_polling(drop_pending_updates=True, stop_signals=None)

def main():
    print("🚀 Bot ko background thread me bhej rahe hain...", flush=True)
    t = Thread(target=run_bot, daemon=True)
    t.start()
    print("🚀 Flask Web Server ko Main Thread me start kar rahe hain...", flush=True)
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port, use_reloader=False)

if __name__ == "__main__":
    main()
