import os
import logging
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

# --- CONFIGURATION ---
BOT_TOKEN = "8151979678:AAFWTg45jDtob6dn6OqAN4qaPCN9ZLB922k"
ADMIN_ID = 1936430807 # <--- Yahan apni asli ID daalein
BUTTON_1_TEXT = "🔥 Premium Videos free"
BUTTON_2_TEXT = "🎬 Free Videos"
BUTTON_1_LINK = "https://t.me/+O27nU16V5VszYjg1"
BUTTON_2_LINK = "https://t.me/+bJy06wHUl79mYWM1"

USER_FILE = "users.txt"

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
    add_user(user_id) # User save ho jayega
    
    bot_username = (await context.bot.get_me()).username
    welcome_msg = (
        f"👋 **Hello {user_name}!**\n\n"
        "Main ek **Auto Join Accept** bot hoon. Mujhe apne Channel ya Group mein niche diye gaye buttons se add karein aur Admin banayein!"
    )
    
    keyboard = [
        [InlineKeyboardButton("➕ Add to Channel", url=f"https://t.me/{bot_username}?startchannel=true")],
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/KobraMethod")]
    ]
    await update.message.reply_text(text=welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Admin Commands
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("👑 **Admin Menu**\n\n/stats - Check total users\n/broadcast [msg] - Message to all")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = get_users()
    await update.message.reply_text(f"📊 **Total Users:** {len(users)}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    msg_to_send = " ".join(context.args)
    if not msg_to_send:
        await update.message.reply_text("❌ Msg likhein: `/broadcast Hello`")
        return

    users = get_users()
    count = 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=int(user), text=msg_to_send)
            count += 1
        except:
            pass
    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")

# Join Request Handler
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.chat_join_request.from_user
        add_user(user.id) # Join request par bhi user ID save hogi
        await update.chat_join_request.approve()
        
        welcome_text = "✅ **Request Accepted!**\n\nNeeche buttons se free content dekho 👇"
        keyboard = [
            [InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK)],
            [InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK)]
        ]
        await context.bot.send_message(chat_id=user.id, text=welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        print(f"Error: {e}")

def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(ChatJoinRequestHandler(join_request))
    
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
