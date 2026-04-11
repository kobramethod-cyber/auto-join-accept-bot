import os
import logging
import json
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, CommandHandler, ContextTypes

# --- RENDER PORT FIX ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Online!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION & LINKS PERSISTENCE ---
BOT_TOKEN = "8151979678:AAFWTg45jDtob6dn6OqAN4qaPCN9ZLB922k"
ADMIN_ID = 1936430807
USER_FILE = "users.txt"
LINKS_FILE = "links.json"

# Default values agar file na ho
def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r') as f:
            return json.load(f)
    return {
        "b1_txt": "🔥 Premium Videos free",
        "b1_url": "https://t.me/+O27nU16V5VszYjg1",
        "b2_txt": "🎬 Free Videos",
        "b2_url": "https://t.me/+bJy06wHUl79mYWM1"
    }

def save_links(data):
    with open(LINKS_FILE, 'w') as f:
        json.dump(data, f)

# --- DATABASE LOGIC ---
def add_user(user_id):
    if not os.path.exists(USER_FILE):
        open(USER_FILE, 'w').close()
    with open(USER_FILE, 'r') as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, 'a') as f:
            f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, 'r') as f:
        return f.read().splitlines()

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    add_user(user_id)
    
    bot_username = (await context.bot.get_me()).username
    welcome_msg = f"👋 **Hello {user_name}!**\n\nMain ek **Auto Join Accept** bot hoon."
    
    keyboard = [
        [InlineKeyboardButton("➕ Add to Channel", url=f"https://t.me/{bot_username}?startchannel=true")],
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/KobraMethod")]
    ]
    await update.message.reply_text(text=welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    menu = (
        "👑 **Admin Menu**\n\n"
        "/stats - Check users\n"
        "/broadcast [msg] - Send to all\n"
        "/setlink [1/2] [Name] [URL] - Change buttons"
    )
    await update.message.reply_text(menu)

async def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        # Format: /setlink 1 Google https://google.com
        btn_num = context.args[0]
        name = context.args[1]
        url = context.args[2]
        
        links = load_links()
        if btn_num == "1":
            links["b1_txt"], links["b1_url"] = name, url
        elif btn_num == "2":
            links["b2_txt"], links["b2_url"] = name, url
        
        save_links(links)
        await update.message.reply_text(f"✅ Button {btn_num} updated!")
    except:
        await update.message.reply_text("❌ Format: `/setlink 1 Name URL`", parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_users()
    await update.message.reply_text(f"📊 **Total Users:** {len(users)}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    msg = " ".join(context.args)
    if not msg: return await update.message.reply_text("Msg likho!")
    
    users = get_users()
    count = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=int(u), text=msg)
            count += 1
        except: pass
    await update.message.reply_text(f"✅ Sent to {count} users.")

# Join Request Handler (Accepts Old & New)
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.chat_join_request.from_user
        add_user(user.id)
        await update.chat_join_request.approve()
        
        links = load_links()
        welcome_text = "✅ **Request Accepted!**\n\nNeeche buttons se content dekho 👇"
        keyboard = [
            [InlineKeyboardButton(links["b1_txt"], url=links["b1_url"])],
            [InlineKeyboardButton(links["b2_txt"], url=links["b2_url"])]
        ]
        await context.bot.send_message(chat_id=user.id, text=welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Join Error: {e}")

def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("setlink", set_link))
    application.add_handler(ChatJoinRequestHandler(join_request))
    
    # drop_pending_updates=False taaki purani requests bhi process hon
    application.run_polling(drop_pending_updates=False)

if __name__ == "__main__":
    main()
