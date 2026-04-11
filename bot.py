import os
import json
import logging
from flask import Flask
from threading import Thread
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, CommandHandler, ContextTypes

# --- MONGO DB SETUP ---
MONGO_URL = "mongodb+srv://Kobra:Kartik9307@cluster0.oxqflcj.mongodb.net/premium_bot?retryWrites=true&w=majority"
client = MongoClient(MONGO_URL)
db = client['premium_bot']
users_col = db['users']
links_col = db['links']

# --- FLASK SERVER ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Online!"

def run():
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION ---
BOT_TOKEN = "8151979678:AAFWTg45jDtob6dn6OqAN4qaPCN9ZLB922k"
ADMIN_ID = 1936430807

# --- DATABASE LOGIC (MongoDB) ---
def add_user_to_db(user_id):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id})

def get_stats():
    return users_col.count_documents({})

def load_links():
    links = links_col.find_one({"id": "config"})
    if links:
        return links
    return {
        "b1_t": "🔥 Premium Videos free",
        "b1_u": "https://t.me/+fCJyhRE921UzOGY1",
        "b2_t": "🎬 Free Videos",
        "b2_u": "https://t.me/+WL7RIg1AXcAyYzZl"
    }

def save_links(b1_t, b1_u, b2_t, b2_u):
    links_col.update_one(
        {"id": "config"},
        {"$set": {"b1_t": b1_t, "b1_u": b1_u, "b2_t": b2_t, "b2_u": b2_u}},
        upsert=True
    )

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user_to_db(user_id)
    
    bot_username = (await context.bot.get_me()).username
    keyboard = [
        [InlineKeyboardButton("➕ Add to Channel", url=f"https://t.me/{bot_username}?startchannel=true")],
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/KobraMethod")]
    ]
    await update.message.reply_text(
        text=f"👋 **Hello {update.effective_user.first_name}!**\nMain ek Auto Join Accept bot hoon.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.chat_join_request.from_user
        await update.chat_join_request.approve()
        add_user_to_db(user.id)

        links = load_links()
        keyboard = [
            [InlineKeyboardButton(links["b1_t"], url=links["b1_u"])],
            [InlineKeyboardButton(links["b2_t"], url=links["b2_u"])]
        ]
        await context.bot.send_message(
            chat_id=user.id,
            text="✅ **Request Accepted!**\n\nNeeche buttons se free content dekho 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error: {e}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(
        "👑 **Admin Menu**\n\n/stats - Check Users\n/broadcast [msg]\n/setlink [1/2] [Name] [URL]"
    )

async def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        num, name, url = context.args[0], context.args[1], context.args[2]
        l = load_links()
        if num == "1":
            save_links(name, url, l.get('b2_t'), l.get('b2_u'))
        else:
            save_links(l.get('b1_t'), l.get('b1_u'), name, url)
        await update.message.reply_text(f"✅ Button {num} updated in Database!")
    except:
        await update.message.reply_text("❌ Usage: `/setlink 1 Name URL`")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    count = get_stats()
    await update.message.reply_text(f"📊 **Total Users in DB:** {count}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    msg = " ".join(context.args)
    if not msg: return
    
    users = users_col.find()
    count = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u['user_id'], text=msg)
            count += 1
        except: pass
    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")

def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("setlink", set_link))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(ChatJoinRequestHandler(join_request))
    
    # False means it will process old requests since bot was offline
    application.run_polling(drop_pending_updates=False)

if __name__ == "__main__":
    main()
