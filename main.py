import logging
import asyncio
import os
import time
from threading import Thread
from flask import Flask
from telegram import Update, ChatPermissions
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
OWNER_NAME = "@Dark_a09"

# 🔹 Bad words load karna
try:
    with open("bad_words.txt", "r", encoding="utf-8") as f:
        BAD_WORDS = [line.strip().lower() for line in f.readlines() if line.strip()]
except FileNotFoundError:
    BAD_WORDS = ["mc", "bc", "madarchod", "behenchod"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🚀 BUG FIX & TRACKERS
background_tasks = set()
user_warnings = {}  # Format: {(chat_id, user_id): warning_count}

# --- ⏱️ TIMERS ---
async def delete_after_time(bot, chat_id, message_id, sleep_time):
    await asyncio.sleep(sleep_time)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# --- ⬛ STYLISH MESSAGE SENDER (BLOCKQUOTE STYLE - NO COPY CODE BUTTON) ---
async def send_stylish_message(bot, chat_id, text):
    # 'blockquote' tag use kiya hai jisse stylish left-border aayega aur copy code button nahi aayega
    formatted_message = f"""<blockquote>{text}\n\n⏳ <i>(Auto-delete in 1 minute)</i></blockquote>"""
    try:
        msg = await bot.send_message(chat_id=chat_id, text=formatted_message, parse_mode="HTML")
        # Naya 1 Minute (60 Seconds) ka Auto-Delete timer
        task = asyncio.create_task(delete_after_time(bot, chat_id, msg.message_id, 60))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
    except Exception as e:
        logging.error(f"Send Error: {e}")

# --- 👑 ADMIN CHECKER ---
async def is_user_admin(chat_id, user_id, bot):
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id == user_id:
                return True
        return False
    except Exception:
        return False

# --- 1️⃣ START COMMAND (ALL RULES INCLUDED) ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mention = update.effective_user.first_name if update.effective_user.first_name else "User"
    chat_title = update.effective_chat.title if update.effective_chat.title else "Group"
    
    start_text = f"""<b>HELLO {mention}! 👋</b>

Main ek Group Manager Bot hoon. Main <b>{chat_title}</b> ko clean aur secure rakhne me madad karta hoon.

🛠 <b>MERA KAAM AUR RULES:</b>
🛑 <b>Anti-Abuse:</b> 3 Warnings ke baad 24 hours Mute!
🔗 <b>Link Protection:</b> Unauthorized links turant delete.
✏️ <b>No Editing:</b> Edited messages allowed nahi.
🧹 <b>Chat Cleaner:</b> Voice/Video chat aur Join/Leave notifications 2 sec me delete.
⏳ <b>Auto-Clean:</b> Group ka har message (photo/text/voice) 5 hours me delete.
👑 <b>Admin Bypass:</b> Admins par koi rule laagu nahi.

⚠️ <b>ZAROORI SOOCHNA:</b>
Mujhe theek se kaam karne ke liye saari Admin Permissions chahiye (Delete msg, Ban users, etc.)

— Admin: {OWNER_NAME}"""
    
    await send_stylish_message(context.bot, update.message.chat.id, start_text)

# --- 2️⃣ ALL SYSTEM NOTIFICATIONS HANDLER (2 SECONDS DELETE) ---
async def system_notification_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        # 2 Second me delete karne ka task (Voice chat, video chat, join, leave etc.)
        task = asyncio.create_task(delete_after_time(context.bot, update.message.chat.id, update.message.message_id, 2))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    # Agar koi naya member add hota hai toh Welcome Message (1 Min auto-delete)
    if update.message and update.message.new_chat_members:
        chat_title = update.message.chat.title if update.message.chat.title else "Group"
        for member in update.message.new_chat_members:
            if member.id == context.bot.id: 
                continue
            username_display = f"@{member.username}" if member.username else "No Username"
            first_name = member.first_name if member.first_name else "Unknown"
            
            welcome_text = f"""⚠️ <b>SYSTEM ALERT: BREACH DETECTED</b> ⚠️

[>] Connection secured to ◖ <b>{chat_title}</b> ◗
[>] Decrypting user signature... SUCCESS.

Welcome to the underground grid, <b>{first_name}</b>.
🆔 Sys_ID : <code>{member.id}</code>
✈️ Tag : {username_display}

[!] Stay stealthy. The logs are active. 👁️‍🗨️
— Admin: {OWNER_NAME}"""
            
            await send_stylish_message(context.bot, update.message.chat.id, welcome_text)

# --- 3️⃣ EDITED MESSAGE HANDLER ---
async def edited_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.edited_message.from_user
    chat_id = update.edited_message.chat.id
    chat_title = update.edited_message.chat.title if update.edited_message.chat.title else "Group"
    
    is_admin = await is_user_admin(chat_id, user.id, context.bot)
    if is_admin:
        return

    try: 
        await update.edited_message.delete()
    except Exception: 
        pass
        
    username_display = f"@{user.username}" if user.username else user.first_name
    
    edit_text = f"""🛑 <b>SYSTEM ALERT: {chat_title}</b> 🛑

[!] Target: {username_display}
[!] Action: Data Modification (Edited Message)

Tumhari chalaaki pakdi gayi. 
<b>{chat_title}</b> server par message ek baar send hone ke baad edit karna allowed nahi hai.
Rules ko follow karo. ☠️

— Admin: {OWNER_NAME}"""
    
    await send_stylish_message(context.bot, chat_id, edit_text)

# --- 4️⃣ ALL MESSAGES PROCESSOR (GAALI, LINKS & 5-HOUR AUTO DELETE) ---
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    user = update.message.from_user

    # 🔹 POINT 5: HAR EK MESSAGE 5 GHANTE (18000 SECONDS) ME DELETE HOGA
    task_5h = asyncio.create_task(delete_after_time(context.bot, chat_id, message_id, 18000))
    background_tasks.add(task_5h)
    task_5h.add_done_callback(background_tasks.discard)

    # Text check karne ke liye (Gaali ya Link)
    text = update.message.text.lower() if update.message.text else ""
    if not text:
        return # Agar photo/sticker hai toh sirf 5 ghante wala timer lagega, gaali check nahi hogi
        
    chat_title = update.message.chat.title if update.message.chat.title else "Group"
    
    is_admin = await is_user_admin(chat_id, user.id, context.bot)
    if is_admin:
        return

    username_display = f"@{user.username}" if user.username else user.first_name

    # 🔹 POINT 3: 3-STRIKE WARNING SYSTEM (GAALI KELIYE)
    has_bad_word = any(word in text.replace('.',' ').split() for word in BAD_WORDS)
    if has_bad_word:
        try: 
            await update.message.delete()
        except Exception: 
            pass
            
        # Warning count check karna
        user_key = (chat_id, user.id)
        current_warnings = user_warnings.get(user_key, 0) + 1
        user_warnings[user_key] = current_warnings

        if current_warnings >= 3:
            # 3rd Warning -> Mute for 24 Hours
            try:
                mute_time = int(time.time()) + 86400 # Current time + 24 hours
                await context.bot.restrict_chat_member(
                    chat_id, user.id, 
                    permissions=ChatPermissions(can_send_messages=False), 
                    until_date=mute_time
                )
                mute_text = f"""🛑 <b>SYSTEM ALERT: BAN APPLIED</b> 🛑

[!] Target: {username_display}
[!] Reason: 3 Warnings Completed (Abusive Language)

Tumhe <b>24 ghante ke liye MUTE</b> kar diya gaya hai!
Agli baar soch samajh kar baat karna. ☠️

— Admin: {OWNER_NAME}"""
                await send_stylish_message(context.bot, chat_id, mute_text)
                user_warnings[user_key] = 0 # Mute hone ke baad count reset
            except Exception as e:
                logging.error(f"Mute Error: {e}")
        else:
            # 1st or 2nd Warning
            warn_text = f"""⚠️ <b>SYSTEM WARNING ({current_warnings}/3)</b> ⚠️

[!] Target: {username_display}
[!] Action: Abusive Language Detected

Apni bhasha sudharein. 
Ye tumhari Warning no. <b>{current_warnings}</b> hai. 3 Warning par 24 hours ke liye MUTE ho jaoge. ☠️

— Admin: {OWNER_NAME}"""
            await send_stylish_message(context.bot, chat_id, warn_text)
        return 

    # 🔹 LINK HANDLER
    has_link = "http://" in text or "https://" in text or "t.me/" in text or ".com" in text
    if has_link:
        try: 
            await update.message.delete()
        except Exception: 
            pass
            
        link_text = f"""🛑 <b>SYSTEM ALERT: {chat_title}</b> 🛑

[!] Target: {username_display}
[!] Action: Unauthorized Link Detected

Tumhari chalaaki pakdi gayi. 
Server par links bhejna sirf Admins ko allowed hai. ☠️

— Admin: {OWNER_NAME}"""
        await send_stylish_message(context.bot, chat_id, link_text)

# --- BOT KO BACKGROUND ME CHALANE WALA FUNCTION ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.ALL, system_notification_handler))
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
