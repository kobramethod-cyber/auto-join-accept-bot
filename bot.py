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
BUTTON_1_TEXT = "🔥 Premium Videos free"
BUTTON_2_TEXT = "🎬 Free Videos"
BUTTON_1_LINK = "https://t.me/+O27nU16V5VszYjg1"
BUTTON_2_LINK = "https://t.me/+bJy06wHUl79mYWM1"

# --- HANDLERS ---

# START Command with Add Buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    bot_username = (await context.bot.get_me()).username
    
    welcome_msg = (
        f"👋 **Hello {user_name}!**\n\n"
        "Main ek **Auto Join Accept** bot hoon. Mujhe apne Channel ya Group mein niche diye gaye buttons se add karein aur Admin banayein!"
    )
    
    # Stylish Buttons for Start
    keyboard = [
        [InlineKeyboardButton("➕ Add to Channel", url=f"https://t.me/{bot_username}?startchannel=true")],
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/KobraMethod")] # Aap apna link daal sakte hain
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text=welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

# Join Request Handler (Accept + Welcome DM)
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.chat_join_request.approve()
        user_id = update.chat_join_request.from_user.id
        
        welcome_text = "✅ **Request Accepted!**\n\nNeeche buttons se free content dekho 👇"
        keyboard = [
            [InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK)],
            [InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=welcome_text,
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
    
    print("Bot is starting with Buttons...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
