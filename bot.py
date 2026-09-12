import os
import json
import logging
import asyncio
from flask import Flask
from threading import Thread
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, CommandHandler, ContextTypes

# --- LOGGING SETUP ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MONGO DB SETUP ---
MONGO_URL = "mongodb+srv://Kobra:Kartik9307@cluster0.oxqflcj.mongodb.net/premium_bot?retryWrites=true&w=majority"
client = MongoClient(MONGO_URL)
db = client['premium_bot']
users_col = db['users']
links_col = db['links']
admins_col = db['admins']  # [CHANGED] Added admins collection for Multi-Admin system

# --- CONFIGURATION ---
BOT_TOKEN = "8151979678:AAHjmJX5UFL1kfM4HYkEdPPLkTJ31GBUF64"
ADMIN_ID = 1936430807  # Main Bot Owner ID

# Ensure main owner is always present in the admins collection upon startup
if not admins_col.find_one({"user_id": ADMIN_ID}):
    admins_col.update_one(
        {"user_id": ADMIN_ID},
        {"$set": {"user_id": ADMIN_ID, "role": "owner"}},
        upsert=True
    )

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
    t.daemon = True
    t.start()

# --- DATABASE & AUTH LOGIC (MongoDB) ---
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

# [CHANGED] Helper functions for Multi-Admin verification
def is_admin(user_id: int) -> bool:
    """Check if user exists in admins collection."""
    return admins_col.find_one({"user_id": user_id}) is not None

def is_owner(user_id: int) -> bool:
    """Check if user is the main fixed owner."""
    return user_id == ADMIN_ID


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
    """
    Automatically approves incoming chat join requests.
    
    NOTE ON OLD PENDING JOIN REQUESTS & RESTART HANDLING:
    - By setting `drop_pending_updates=False` in `run_polling`, the bot processes 
      pending updates that arrived while it was offline.
    - Telegram Bot API Limitation: The Telegram API does not allow bots to fetch 
      historical pre-existing join requests via a direct API call (like `getChatJoinRequests`) 
      unless those requests send an update or are re-triggered. However, setting 
      `drop_pending_updates=False` ensures that pending updates waiting in Telegram's 
      queue when the bot restarts are processed immediately.
    """
    async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.chat_join_request
        if not query:
            return

        user = query.from_user
        await query.approve()
        add_user_to_db(user.id)

        links = load_links()
        keyboard = [
            [InlineKeyboardButton(links["b1_t"], url=links["b1_u"])],
            [InlineKeyboardButton(links["b2_t"], url=links["b2_u"])]
        ]

        try:
            await context.bot.send_message(
                chat_id=user.id,
                text="✅ Request Accepted!\n\nNeeche buttons se free content dekho 👇",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            logger.info(f"DM sent successfully to {user.id}")

        except Exception as e:
            logger.exception(f"DM FAILED for {user.id}: {e}")

    except Exception as e:
        logger.error(f"Error handling join request: {e}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id): 
        return
    
    await update.message.reply_text(
        "👑 **Admin Menu**\n\n"
        "/stats - Check Users & Admins\n"
        "/broadcast [msg] - Send broadcast to users\n"
        "/setlink [1/2] [Name] [URL] - Update buttons\n"
        "/addadmin [USER_ID] - Add new admin (Owner only)\n"
        "/removeadmin [USER_ID] - Remove admin (Owner only)\n"
        "/admins - View all admins",
        parse_mode="Markdown"
    )

async def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id): 
        return
    try:
        num, name, url = context.args[0], context.args[1], context.args[2]
        l = load_links()
        if num == "1":
            save_links(name, url, l.get('b2_t'), l.get('b2_u'))
        else:
            save_links(l.get('b1_t'), l.get('b1_u'), name, url)
        await update.message.reply_text(f"✅ Button {num} updated in Database!")
    except Exception:
        await update.message.reply_text("❌ Usage: `/setlink 1 Name URL`", parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id): 
        return
    count = get_stats()
    admin_count = admins_col.count_documents({})
    await update.message.reply_text(
        f"📊 **Bot Statistics:**\n\n"
        f"👥 Total Users in DB: `{count}`\n"
        f"🛡️ Total Admins: `{admin_count}`",
        parse_mode="Markdown"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id): 
        return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("⚠️ Please provide a message to broadcast.")
        return
    
    users = users_col.find()
    count = 0
    status_msg = await update.message.reply_text("📢 Broadcasting started...")
    
    for u in users:
        try:
            await context.bot.send_message(chat_id=u['user_id'], text=msg)
            count += 1
            await asyncio.sleep(0.04)  # Flood control
        except Exception: 
            pass
            
    await status_msg.edit_text(f"✅ Broadcast successfully sent to `{count}` users.", parse_mode="Markdown")


# --- NEW ADMIN MANAGEMENT COMMANDS (Owner Only) ---

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the main bot owner can add new admins.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/addadmin USER_ID`", parse_mode="Markdown")
        return

    try:
        new_admin_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID. Please provide a numeric ID.")
        return

    if admins_col.find_one({"user_id": new_admin_id}):
        await update.message.reply_text("⚠️ This user is already an admin.")
        return

    admins_col.insert_one({"user_id": new_admin_id, "role": "admin"})
    await update.message.reply_text(f"✅ Successfully added `{new_admin_id}` as an admin.", parse_mode="Markdown")


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the main bot owner can remove admins.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/removeadmin USER_ID`", parse_mode="Markdown")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID.")
        return

    if target_id == ADMIN_ID:
        await update.message.reply_text("❌ You cannot remove the main bot owner.")
        return

    result = admins_col.delete_one({"user_id": target_id})
    if result.deleted_count > 0:
        await update.message.reply_text(f"✅ Successfully removed `{target_id}` from admins.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ User ID not found in the admin list.")


async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ You are not authorized to view the admin list.")
        return

    all_admins = list(admins_col.find({}))
    text = "👑 **Bot Admin List:**\n\n"
    for admin in all_admins:
        role = admin.get("role", "admin")
        text += f"• `{admin['user_id']}` ({role})\n"

    await update.message.reply_text(text, parse_mode="Markdown")


def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Register command and request handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("setlink", set_link))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("addadmin", add_admin))
    application.add_handler(CommandHandler("removeadmin", remove_admin))
    application.add_handler(CommandHandler("admins", list_admins))
    
    application.add_handler(ChatJoinRequestHandler(join_request))
    
    # drop_pending_updates=False ensures pending requests/updates accumulated while offline are processed on restart
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)

if __name__ == "__main__":
    main()
