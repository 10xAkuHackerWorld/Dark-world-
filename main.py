import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# 🔹 Aapka Bot Token
TOKEN = "8603465694:AAE_lfAe6SbOEbC7hbzDkAfwV_JhaPqFhro"
OWNER_NAME = "Admin"

# 🔹 Gaaliyon ki list
BAD_WORDS = ["mc", "bc", "madarchod", "behenchod", "maa", "baap", "kutta", "kaminey", "saala"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- ⏱️ 30 MINUTES BAAD BOT KA MESSAGE DELETE KARNE WALA TIMER ---
async def delete_after_30_mins(bot, chat_id, message_id):
    await asyncio.sleep(1800)  # 1800 seconds = 30 minutes
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# --- ⏱️ 3 SECONDS BAAD SYSTEM NOTIFICATION DELETE KARNE WALA TIMER ---
async def delete_system_msg(bot, chat_id, message_id):
    await asyncio.sleep(3)  # 3 seconds delay
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.error(f"System msg delete error: {e}")

# --- ⬛ BACKGROUND BOX AUR TIMER KE SATH MESSAGE BHEJNA ---
async def send_dark_message(bot, chat_id, text):
    # Sirf ``` lagane se 'text' likha nahi aayega aur ekdum saaf dark box banega
    formatted_message = f"""```
{text}

⌛ (Auto-delete in 30 minutes)
```"""
    try:
        # Standard Markdown use kar rahe hain taaki koi format error na aaye
        msg = await bot.send_message(chat_id=chat_id, text=formatted_message, parse_mode="Markdown")
        # Message bhejte hi 30 mins (1800 sec) ki ulti ginti shuru
        asyncio.create_task(delete_after_30_mins(bot, chat_id, msg.message_id))
    except Exception as e:
        logging.error(f"Send Error: {e}")

# --- 👑 ADMIN & OWNER CHECKER ---
async def is_user_admin(chat_id, user_id, bot):
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id == user_id:
                return True
        return False
    except Exception:
        return False

# --- 1️⃣ START COMMAND (Updated with Full Features List) ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mention = user.first_name if user.first_name else "User"
    
    start_text = f"""Hello {mention}! 👋

Main ek Group Manager Bot hoon. Main aapke group ko clean aur secure rakhne me madad karta hoon.

🛠 Mera Kaam (Bot Features):
🛑 Anti-Abuse: Gaali/Bad words wale messages turant delete.
🔗 Link Protection: Group me bheji gayi un-authorized links turant delete.
✏️ No Editing: Message send hone ke baad edit karna allowed nahi hai (Edited msg delete).
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

# --- 2️⃣ NEW MEMBER HANDLER ("Joined the group" ko 3 sec me delete aur Welcome msg) ---
async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        asyncio.create_task(delete_system_msg(context.bot, update.message.chat.id, update.message.message_id))
    
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: 
            continue
            
        username_display = f"@{member.username}" if member.username else "No Username"
        first_name = member.first_name if member.first_name else "Unknown"
        
        welcome_text = f"""╔═════════════════════════════════╗
║ ⚠️ 𝗦𝗬𝗦𝗧𝗘𝗠 𝗔𝗟𝗘𝗥𝗧: 𝗕𝗥𝗘𝗔𝗖𝗛 𝗗𝗘𝗧𝗘𝗖𝗧𝗘𝗗 ⚠️ ║
╚═════════════════════════════════╝
[>] Connection secured to ◖ DARK WORLD ◗.
[>] Decrypting user signature... SUCCESS.

Welcome to the underground grid, {first_name}.

┌─[ USER DATABASE LOG ]───────┐
│ 👤 Alias  : {first_name}
│ 🆔 Sys_ID : {member.id}
│ ✈️ Tag    : {username_display}
└─────────────────────────────┘

[!] Stay stealthy. The logs are active. 👁️‍🗨️"""
        
        await send_dark_message(context.bot, update.message.chat.id, welcome_text)

# --- 3️⃣ LEFT MEMBER HANDLER ("Left the group" ko 3 sec me delete karega) ---
async def left_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        asyncio.create_task(delete_system_msg(context.bot, update.message.chat.id, update.message.message_id))

# --- 4️⃣ EDITED MESSAGE HANDLER ---
async def edited_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.edited_message.from_user
    chat_id = update.edited_message.chat.id
    
    is_admin = await is_user_admin(chat_id, user.id, context.bot)
    if is_admin:
        return

    try: 
        await update.edited_message.delete()
    except Exception: 
        pass
        
    username_display = f"@{user.username}" if user.username else user.first_name
    
    edit_text = f"""╔═════════════════════════════════╗
║ 🛑 DARK WORLD: SYSTEM ALERT 🛑  ║
╚═════════════════════════════════╝
[!] Target: {username_display}
[!] Action: Data Modification (Edited Message)

Tumhari chalaaki pakdi gayi. 
DARK WORLD server par message ek baar send hone ke baad edit karna allowed nahi hai.

>> Original message hamare database me save ho chuka hai.
>> Rules ko follow karo, warna system tumhe bahar nikal dega. ☠️

— Admin: dark"""
    
    await send_dark_message(context.bot, chat_id, edit_text)

# --- 5️⃣ GAALI AUR LINK HANDLER ---
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: 
        return
        
    user = update.message.from_user
    chat_id = update.message.chat.id
    text = update.message.text.lower()
    
    is_admin = await is_user_admin(chat_id, user.id, context.bot)
    if is_admin:
        return

    username_display = f"@{user.username}" if user.username else user.first_name

    # Check 1: Gaali
    has_bad_word = any(word in text.replace('.',' ').split() for word in BAD_WORDS)
    if has_bad_word:
        try: 
            await update.message.delete()
        except Exception: 
            pass
            
        warn_text = f"""╔═════════════════════════════════╗
║ 🛑 DARK WORLD: SYSTEM ALERT 🛑  ║
╚═════════════════════════════════╝
[!] Target: {username_display}
[!] Action: Abusive Language Detected

Aapne DARK WORLD ke strict rules tode hain. 
Abusive language yahan bilkul tolerate nahi ki jayegi.

[ ERROR ] Apni bhasha sudharein.
Agli galti par seedha DARK WORLD se bahar nikal diya jayega. ☠️

— Admin: dark"""
        
        await send_dark_message(context.bot, chat_id, warn_text)
        return 

    # Check 2: Links
    has_link = "http://" in text or "https://" in text or "t.me/" in text or ".com" in text
    if has_link:
        try: 
            await update.message.delete()
        except Exception: 
            pass
            
        link_text = f"""╔═════════════════════════════════╗
║ 🛑 DARK WORLD: SYSTEM ALERT 🛑  ║
╚═════════════════════════════════╝
[!] Target: {username_display}
[!] Action: Unauthorized Link Detected

Tumhari chalaaki pakdi gayi. 
DARK WORLD server par links bhejna sirf Admins ko allowed hai.

>> Rules ko follow karo, warna system tumhe bahar nikal dega. ☠️

— Admin: dark"""
        
        await send_dark_message(context.bot, chat_id, link_text)

# --- BOT RUNNER ---
def main():
    print("🚀 DARK WORLD Bot Started (Updated Start Features List) ...")
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member_handler))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited_message_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.EDITED_MESSAGE, process_message))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
