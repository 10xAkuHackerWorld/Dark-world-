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
user_warnings = {}  
USER_CACHE = {}     

# --- ⏱️ TIMERS ---
async def delete_after_time(bot, chat_id, message_id, sleep_time):
    await asyncio.sleep(sleep_time)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# --- ⬛ STYLISH MESSAGE SENDER ---
async def send_stylish_message(bot, chat_id, text, auto_delete=True):
    # Ping aur ID commands ke liye auto-delete optional kar diya hai
    if auto_delete:
        formatted_message = f"""<blockquote>{text}\n\n⏳ <i>(Auto-delete in 1 minute)</i></blockquote>"""
    else:
        formatted_message = f"""<blockquote>{text}</blockquote>"""
        
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

# --- 1️⃣ START COMMAND ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mention = update.effective_user.first_name if update.effective_user.first_name else "User"
    chat_title = update.effective_chat.title if update.effective_chat.title else "Group"
    
    start_text = f"""<b>HELLO {mention}! 👋</b>

Main ek Group Manager Bot hoon. Main <b>{chat_title}</b> ko clean aur secure rakhne me madad karta hoon.

🛠 <b>MERA KAAM AUR RULES:</b>
🛑 <b>Anti-Abuse:</b> Members ko 3 Warning, Admins ko 5 Warning. Fir 24 hours MUTE!
🔗 <b>Link Protection:</b> Unauthorized links turant delete.
✏️ <b>No Editing:</b> Edited messages allowed nahi.
🧹 <b>Chat Cleaner:</b> System notifications 2 sec me delete.
⏳ <b>Auto-Clean:</b> Group ka har message 5 hours me delete.
🔓 <b>Unmute System:</b> /unmute command se ban hatayein.
🏓 <b>Ping & Info:</b> /ping aur /id commands available.

— Admin: {OWNER_NAME}"""
    
    await send_stylish_message(context.bot, update.message.chat.id, start_text)

# --- 2️⃣ PING COMMAND ---
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("<i>Pinging server...</i>", parse_mode="HTML")
    end_time = time.time()
    
    ping_time = round((end_time - start_time) * 1000)
    ping_text = f"🏓 <b>PONG!</b>\n\n⚡ Latency: <b>{ping_time}ms</b>\n🤖 Status: <b>Alive & Active</b>\n\n— Admin: {OWNER_NAME}"
    
    try:
        await msg.delete()
    except:
        pass
    await send_stylish_message(context.bot, update.message.chat.id, ping_text, auto_delete=False)

# --- 3️⃣ ID COMMAND ---
async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.effective_user
    chat_id = update.message.chat.id
    
    # Agar kisi message par reply kiya hai
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user

    user_id = target_user.id
    first_name = target_user.first_name if target_user.first_name else "N/A"
    last_name = target_user.last_name if target_user.last_name else "N/A"
    username = f"@{target_user.username}" if target_user.username else "N/A"
    
    info_text = f"""🕵️‍♂️ <b>USER INFORMATION</b> 🕵️‍♂️

👤 <b>First Name:</b> {first_name}
👤 <b>Last Name:</b> {last_name}
🔗 <b>Username:</b> {username}
🆔 <b>User ID:</b> <code>{user_id}</code>
💬 <b>Chat ID:</b> <code>{chat_id}</code>

<i>Note: Phone numbers are hidden by Telegram Privacy Policy.</i>"""
    
    await send_stylish_message(context.bot, chat_id, info_text, auto_delete=False)

# --- 4️⃣ UNMUTE COMMAND ---
async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_id = update.effective_user.id
    
    status = await get_user_status(chat_id, user_id, context.bot)
    if status != 'creator':
        await send_stylish_message(context.bot, chat_id, "🛑 <b>ACCESS DENIED!</b>\n\nYe command sirf Group Owner use kar sakta hai!")
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
    else:
        await send_stylish_message(context.bot, chat_id, "⚠️ Kisko unmute karna hai? Reply karo ya <code>/unmute @username</code> likho.")
        return

    if not target_user_id:
        await send_stylish_message(context.bot, chat_id, "⚠️ User data nahi mila! Reply karke try karein.")
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
        await send_stylish_message(context.bot, chat_id, f"✅ <b>TARGET UNMUTED!</b>\n\n[!] Target: {display_name}\n[!] Action: Unmuted by Owner.")
    except Exception as e:
        logging.error(f"Unmute Error: {e}")

# --- 5️⃣ WELCOME MESSAGE HANDLER ---
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = asyncio.create_task(delete_after_time(context.bot, update.message.chat.id, update.message.message_id, 2))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

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
    chat_title = update.edited_message.chat.title if update.edited_message.chat.title else "Group"
    
    status = await get_user_status(chat_id, user.id, context.bot)
    if status in ['creator', 'administrator']:
        return

    try: 
        await update.edited_message.delete()
    except Exception: 
        pass
        
    username_display = f"@{user.username}" if user.username else user.first_name
    edit_text = f"""🛑 <b>SYSTEM ALERT: {chat_title}</b> 🛑\n\n[!] Target: {username_display}\n[!] Action: Data Modification (Edited Message)\n\nTumhari chalaaki pakdi gayi. \n<b>{chat_title}</b> server par message edit karna allowed nahi hai.\n\n— Admin: {OWNER_NAME}"""
    await send_stylish_message(context.bot, chat_id, edit_text)

# --- 8️⃣ ALL MESSAGES PROCESSOR ---
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
        
    chat_title = update.message.chat.title if update.message.chat.title else "Group"
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
                await context.bot.restrict_chat_member(
                    chat_id, user.id, 
                    permissions=ChatPermissions(can_send_messages=False), 
                    until_date=mute_time
                )
                mute_text = f"""🛑 <b>SYSTEM ALERT: BAN APPLIED</b> 🛑\n\n[!] Target: {username_display}\n[!] Reason: {max_warnings} Warnings Completed (Abusive Language)\n\nTumhe <b>24 ghante ke liye MUTE</b> kar diya gaya hai! ☠️\n\n— Admin: {OWNER_NAME}"""
                await send_stylish_message(context.bot, chat_id, mute_text)
                user_warnings[user_key] = 0 
            except Exception as e:
                if "administrators" in str(e).lower():
                    admin_err_text = f"""⚠️ <b>SYSTEM ERROR</b> ⚠️\n\n[!] Target: {username_display}\n\nYe banda Group Admin hai. Meri power Admin ko mute karne ki nahi hai. \nOwner ko iski power chhinni padegi tabhi mute hoga! ☠️"""
                    await send_stylish_message(context.bot, chat_id, admin_err_text)
                    user_warnings[user_key] = 0
        else:
            warn_text = f"""⚠️ <b>SYSTEM WARNING ({current_warnings}/{max_warnings})</b> ⚠️\n\n[!] Target: {username_display}\n[!] Action: Abusive Language Detected\n\nApni bhasha sudharein. \nYe tumhari Warning no. <b>{current_warnings}</b> hai. {max_warnings} Warning par 24 hours ke liye MUTE ho jaoge. ☠️\n\n— Admin: {OWNER_NAME}"""
            await send_stylish_message(context.bot, chat_id, warn_text)
        return 

    if status not in ['creator', 'administrator']:
        has_link = "http://" in text or "https://" in text or "t.me/" in text or ".com" in text
        if has_link:
            try: 
                await update.message.delete()
            except Exception: 
                pass
            link_text = f"""🛑 <b>SYSTEM ALERT: {chat_title}</b> 🛑\n\n[!] Target: {username_display}\n[!] Action: Unauthorized Link Detected\n\nTumhari chalaaki pakdi gayi. \nServer par links bhejna sirf Admins ko allowed hai. ☠️\n\n— Admin: {OWNER_NAME}"""
            await send_stylish_message(context.bot, chat_id, link_text)

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
