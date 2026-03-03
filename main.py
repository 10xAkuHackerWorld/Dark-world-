import logging
import os
import json
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

# --- FLASK WEB SERVER (Render ke liye zaroori) ---
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_web():
    # Render khud ek PORT deta hai, hume uspe chalana hota hai
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)


# --- BOT CONFIG ---
# 🔹 Yaha apna bot token daalo
TOKEN = "7900700579:AAHCw_LFEbWFh3iWGH9mIm1OGznTkQLMpuc"
OWNER_NAME = "Admin"
USERS_FILE = "users_data.json"

# --- JSON DATA SAVING FUNCTION ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_user(user_id, first_name, username):
    users = load_users()
    users[str(user_id)] = {
        "first_name": first_name,
        "username": username
    }
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)

# --- BAD WORDS FUNCTION ---
def load_bad_words():
    if os.path.exists("bad_words.txt"):
        with open("bad_words.txt", "r", encoding="utf-8") as file:
            return [line.strip().lower() for line in file if line.strip()]
    else:
        # Default list
        return ["mc", "bc", "madarchod", "behenchod", "maa", "baap", "kutta", "kaminey", "saala"]

BAD_WORDS = load_bad_words()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# --- BOT HANDLERS ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mention = f"@{user.username}" if user.username else user.first_name
    save_user(user.id, user.first_name, user.username)

    welcome_message = f"""
Hello {mention}! 👋

Main ek Group Manager Bot hoon. Main aapke group ko clean rakhne me madad karta hoon.

**Mera Kaam:**
🛑 **Anti-Abuse:** Gaali wale messages turant delete.
✏️ **No Editing:** Edited messages turant delete.
👋 **Welcome:** Naye members ka swagat.

Mujhe Admin banayein aur "Delete Messages" ki permission dein!
- Made by {OWNER_NAME}
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue

        save_user(member.id, member.first_name, member.username)

        mention = f"@{member.username}" if member.username else member.first_name
        username_display = f"@{member.username}" if member.username else "No Username"
        
        welcome_text = f"""
Hey there {mention}, and welcome to **DARK WORLD**! How are you?

👤 User: {member.first_name}
🤨 ID: `{member.id}`
✈️ Username: {username_display}
"""
        await context.bot.send_message(chat_id=update.message.chat.id, text=welcome_text, parse_mode="Markdown")

async def check_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text.lower()
    clean_text = text.replace('.', ' ').replace(',', ' ').replace('!', ' ').replace('?', ' ')
    words_in_message = clean_text.split()

    is_bad_word_found = False
    for word in BAD_WORDS:
        if word in words_in_message: 
            is_bad_word_found = True
            break

    if is_bad_word_found:
        user = message.from_user
        save_user(user.id, user.first_name, user.username)

        try:
            await message.delete()
        except Exception as e:
            logging.error(f"Message delete nahi ho paya: {e}")

        mention = f"@{user.username}" if user.username else user.first_name
        warning = f"⚠️ **Warning** ⚠️\n\n{mention}\nAapne galat shabd ka use kiya hai.\nKripya group me tameez se baat karein.\n\n- {OWNER_NAME}"
        
        await context.bot.send_message(chat_id=message.chat.id, text=warning, parse_mode="Markdown")

async def check_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.edited_message
    if not message:
        return

    user = message.from_user
    save_user(user.id, user.first_name, user.username)

    try:
        await message.delete()
    except Exception as e:
        logging.error(f"Edited message delete nahi ho paya: {e}")

    mention = f"@{user.username}" if user.username else user.first_name
    warning = f"⚠️ **Edited Message Warning** ⚠️\n\n{mention}\nGroup me message edit karna allowed nahi hai. Chalaaki nahi chalegi!\n\n- {OWNER_NAME}"
    
    await context.bot.send_message(chat_id=message.chat.id, text=warning, parse_mode="Markdown")

def main():
    # 🔹 Flask web server ko alag thread me start kar rahe hain
    t = Thread(target=run_web)
    t.start()

    # 🔹 Bot ko start kar rahe hain
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.EDITED_MESSAGE, check_bad_words))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, check_edited_message))

    print(f"Bot is running... {len(BAD_WORDS)} bad words loaded.")
    app.run_polling()

if __name__ == "__main__":
    main()
