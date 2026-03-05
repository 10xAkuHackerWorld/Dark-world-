import logging
import asyncio
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# --- FLASK WEB SERVER (Render aur Pulsetic ke liye zaroori) ---
app_web = Flask(__name__)

import logging as flask_logging
flask_logging.getLogger('werkzeug').setLevel(flask_logging.ERROR)

@app_web.route('/')
def home():
    return "Bot is alive and running 24/7 on Render!"

# 🔹 Aapka NAYA Bot Token aur Owner Username Yahan Set Hai
TOKEN = "8603465694:AAE_lfAe6SbOEbC7hbzDkAfwV_JhaPqFhro"
OWNER_NAME = "@Dark_a09"

BAD_WORDS = ["mc", "bc", "madarchod", "behenchod", "maa", "baap", "kutta", "kaminey", "saala"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- TIMERS ---
async def delete_after_30_mins(bot, chat_id, message_id):
    await asyncio.sleep(1800)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

async def delete_system_msg(bot, chat_id, message_id):
    await asyncio.sleep(3)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# --- DARK BOX MESSAGE ---
async def send_dark_message(bot, chat_id, text):
    formatted_message = f"""```
{text}

⌛ (Auto-delete in 30 minutes)
```"""
    try:
        msg = await bot.send_message(chat_id=chat_id, text=formatted_message, parse_mode="Markdown")
        asyncio.create_task(delete_after_30_mins(bot, chat_id, msg.message_id))
    except Exception as e:
        logging.error(f"Send Error: {e}")

# --- ADMIN CHECKER ---
async def is_user_admin(chat_id, user_id, bot):
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id == user_id:
                return True
        return False
    except Exception:
        return False

# --- 1️⃣ START COMMAND ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mention = user.first_name if user.first_name else "User"
    chat_title = update.effective_chat.title if update.effective_chat.title else "Group"
    
    start_text = f"""Hello {mention}! 👋

Main ek Group Manager Bot hoon. Main aapke group ko clean aur secure rakhne me madad karta hoon.

🛠 Mera Kaam (Bot Features):
🛑 Anti-Abuse: Gaali/Bad words wale messages turant delete.
🔗 Link Protection: Group me bheji gayi un-authorized links turant delete.
✏️ No Editing: Message send hone ke baad edit karna allowed nahi hai.
👋 Welcome Message: Naye members aane par stylish welcome message.
🧹 Chat Cleaner: Telegram ke "Joined" aur "Left" wale notification 3 second me gayab.
⏳ Auto-Delete: Mere saare system messages 30 minutes me apne aap delete ho jayenge.
👑 Admin Bypass: Group Owner aur Admins par koi bhi rule laagu nahi hoga.

⚠️ ZAROORI SOOCHNA:
Mujhe kisi bhi group me theek se kaam karne ke liye ye saari ADMIN PERMISSIONS chahiye:

✅ Change Group Info
✅ Delete Messages
✅ Ban Users
✅ Invite Users via Link
✅ Pin Messages
✅ Edit Member Tags
✅ Manage Stories
✅ Manage Live Streams
✅ Add New Admins

Agar ye sab ON nahi hua, toh system theek se work nahi karega!

- Made by {OWNER_NAME}"""
    
    await send_dark_message(context.bot, update.message.chat.id, start_text)

# --- 2️⃣ NEW MEMBER HANDLER ---
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        asyncio.create_task(delete_system_msg(context.bot, update.message.chat.id, update.message.message_id))
    
    chat_title = update.message.chat.title if update.message.chat.title else "Group"

    for member in update.message.new_chat_members:
        if member.id == context.bot.id: 
            continue
            
        username_display = f"@{member.username}" if member.username else "No Username"
        first_name = member.first_name if member.first_name else "Unknown"
        
        welcome_text = f"""╔═════════════════════════════════╗
║ ⚠️ 𝗦𝗬𝗦𝗧𝗘𝗠 𝗔𝗟𝗘𝗥𝗧: 𝗕𝗥𝗘𝗔𝗖𝗛 𝗗𝗘𝗧𝗘𝗖𝗧𝗘𝗗 ⚠️ ║
╚═════════════════════════════════╝
[>] Connection secured to ◖ {chat_title} ◗.
[>] Decrypting user signature... SUCCESS.

Welcome to the underground grid, {first_name}.

┌─[ USER DATABASE LOG ]───────┐
│ 👤 Alias  : {first_name}
│ 🆔 Sys_ID : {member.id}
│ ✈️ Tag    : {username_display}
└─────────────────────────────┘

[!] Stay stealthy. The logs are active. 👁️‍🗨️"""
        
        await send_dark_message(context.bot, update.message.chat.id, welcome_text)

# --- 3️⃣ LEFT MEMBER HANDLER ---
async def left_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        asyncio.create_task(delete_system_msg(context.bot, update.message.chat.id, update.message.message_id))

# --- 4️⃣ EDITED MESSAGE HANDLER ---
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
    
    edit_text = f"""╔═════════════════════════════════╗
║ 🛑 {chat_title.upper()}: SYSTEM ALERT 🛑  ║
╚═════════════════════════════════╝
[!] Target: {username_display}
[!] Action: Data Modification (Edited Message)

Tumhari chalaaki pakdi gayi. 
{chat_title} server par message ek baar send hone ke baad edit karna allowed nahi hai.

>> Original message hamare database me save ho chuka hai.
>> Rules ko follow karo, warna system tumhe bahar nikal dega. ☠️

— Admin: {OWNER_NAME}"""
    
    await send_dark_message(context.bot, chat_id, edit_text)

# --- 5️⃣ GAALI AUR LINK HANDLER ---
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: 
        return
        
    user = update.message.from_user
    chat_id = update.message.chat.id
    text = update.message.text.lower()
    chat_title = update.message.chat.title if update.message.chat.title else "Group"
    
    is_admin = await is_user_admin(chat_id, user.id, context.bot)
    if is_admin:
        return

    username_display = f"@{user.username}" if user.username else user.first_name

    has_bad_word = any(word in text.replace('.',' ').split() for word in BAD_WORDS)
    if has_bad_word:
        try: 
            await update.message.delete()
        except Exception: 
            pass
            
        warn_text = f"""╔═════════════════════════════════╗
║ 🛑 {chat_title.upper()}: SYSTEM ALERT 🛑  ║
╚═════════════════════════════════╝
[!] Target: {username_display}
[!] Action: Abusive Language Detected

Aapne {chat_title} ke strict rules tode hain. 
Abusive language yahan bilkul tolerate nahi ki jayegi.

[ ERROR ] Apni bhasha sudharein.
Agli galti par seedha {chat_title} se bahar nikal diya jayega. ☠️

— Admin: {OWNER_NAME}"""
        await send_dark_message(context.bot, chat_id, warn_text)
        return 

    has_link = "http://" in text or "https://" in text or "t.me/" in text or ".com" in text
    if has_link:
        try: 
            await update.message.delete()
        except Exception: 
            pass
            
        link_text = f"""╔═════════════════════════════════╗
║ 🛑 {chat_title.upper()}: SYSTEM ALERT 🛑  ║
╚═════════════════════════════════╝
[!] Target: {username_display}
[!] Action: Unauthorized Link Detected

Tumhari chalaaki pakdi gayi. 
{chat_title} server par links bhejna sirf Admins ko allowed hai.

>> Rules ko follow karo, warna system tumhe bahar nikal dega. ☠️

— Admin: {OWNER_NAME}"""
        await send_dark_message(context.bot, chat_id, link_text)

# --- BOT KO BACKGROUND ME CHALANE WALA FUNCTION ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member_handler))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited_message_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.EDITED_MESSAGE, process_message))

    print("✅ Telegram Bot running successfully in background!", flush=True)
    app.run_polling(drop_pending_updates=True, stop_signals=None)

# --- MAIN SERVER FUNCTION ---
def main():
    print("🚀 Bot ko background thread me bhej rahe hain...", flush=True)
    t = Thread(target=run_bot, daemon=True)
    t.start()

    print("🚀 Flask Web Server ko Main Thread me start kar rahe hain...", flush=True)
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port, use_reloader=False)

if __name__ == "__main__":
    main()
