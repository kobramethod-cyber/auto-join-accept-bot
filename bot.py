import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, CommandHandler, ContextTypes

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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

# --- CONFIGURATION (Naya Token Updated) ---
BOT_TOKEN = "8151979678:AAFWTg45jDtob6dn6OqAN4qaPCN9ZLB922k"
BUTTON_1_TEXT = "🔥 Premium Videos free"
BUTTON_2_TEXT = "🎬 Free Videos"
BUTTON_1_LINK = "https://t.me/+O27nU16V5VszYjg1"
BUTTON_2_LINK = "https://t.me/+bJy06wHUl79mYWM1"

WELCOME_TEXT = (
    "✅ **Request Accepted!**\n\n"
    "Neeche buttons se free content dekho 👇"
)

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    msg = f"Hello {user_name}!\n\nMujhe apne channel mein Admin banayein, main Join Requests auto-accept kar loonga."
    await update.message.reply_text(msg)

async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.chat_join_request.approve()
        user_id = update.chat_join_request.from_user.id
        keyboard = [
            [InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK)],
            [InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=user_id,
            text=WELCOME_TEXT,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error: {e}")

def main():
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatJoinRequestHandler(join_request))
    
    print("Bot is starting with NEW TOKEN...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
