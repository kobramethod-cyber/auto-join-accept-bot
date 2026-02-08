import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# ===== RENDER PORT FIX (DON'T TOUCH) =====
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    # Render hamesha PORT environment variable mangta hai
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ==========================================

# ===== BOT SETTINGS =====
BOT_TOKEN = "8151979678:AAHonAeiyFTgoKeZqok3OTG5Rc4jnVJRZYs"
BUTTON_1_TEXT = "🔥 Premium Videos free"
BUTTON_2_TEXT = "🎬 Free Videos"
BUTTON_1_LINK = "https://t.me/+O27nU16V5VszYjg1"
BUTTON_2_LINK = "https://t.me/+bJy06wHUl79mYWM1"
WELCOME_TEXT = (
    "✅ **Request Accepted!**\n\n"
    "Neeche buttons se free content dekho 👇"
)

# ===== JOIN REQUEST HANDLER =====
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.chat_join_request.from_user
        # Request Accept karna
        await update.chat_join_request.approve()

        # Buttons banana
        keyboard = [
            [InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK)],
            [InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # User ko message bhejna
        await context.bot.send_message(
            chat_id=user.id,
            text=WELCOME_TEXT,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error: {e}")

# ===== MAIN FUNCTION =====
def main():
    # Pehle Fake Server start karein taaki Render khush rahe
    keep_alive()
    
    # Bot start karein
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(ChatJoinRequestHandler(join_request))
    
    print("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
