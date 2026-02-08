import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# --- YE RENDER KE LIYE ZAROORI HAI ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()
# ------------------------------------

BOT_TOKEN = "8151979678:AAHonAeiyFTgoKeZqok3OTG5Rc4jnVJRZYs"
BUTTON_1_TEXT = "🔥 Premium Videos free"
BUTTON_2_TEXT = "🎬 Free Videos"
BUTTON_1_LINK = "https://t.me/+O27nU16V5VszYjg1"
BUTTON_2_LINK = "https://t.me/+bJy06wHUl79mYWM1"

WELCOME_TEXT = (
    "✅ **Request Accepted!**\n\n"
    "Neeche buttons se free content dekho 👇"
)

async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    await update.chat_join_request.approve()
    keyboard = [[InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK)],
                [InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_message(chat_id=user.id, text=WELCOME_TEXT, reply_markup=reply_markup, parse_mode="Markdown")
    except:
        pass

def main():
    # Ise start command se pehle call karein
    keep_alive() 
    
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(ChatJoinRequestHandler(join_request))
    app_bot.run_polling()

if __name__ == "__main__":
    main()
