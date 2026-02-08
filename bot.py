import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, CommandHandler, ContextTypes

# ===== RENDER PORT FIX =====
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ===========================

BOT_TOKEN = "8151979678:AAHonAeiyFTgoKeZqok3OTG5Rc4jnVJRZYs"

# ===== START COMMAND HANDLER =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_msg = (
        f"👋 **Hello {user_name}!**\n\n"
        "Main ek Auto Join Accept Bot hoon.\n\n"
        "📢 **Mujhe apne Channel ya Group mein Admin banayein.**\n"
        "✅ Main saari join requests turant accept kar loonga!"
    )
    
    keyboard = [
        [InlineKeyboardButton("➕ Add to Channel", url=f"https://t.me/{context.bot.username}?startchannel=true")],
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{context.bot.username}?startgroup=true")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text=welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

# ===== JOIN REQUEST HANDLER =====
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    await update.chat_join_request.approve()
    
    welcome_text = "✅ **Request Accepted!**\n\nNeeche buttons se free content dekho 👇"
    keyboard = [
        [InlineKeyboardButton("🔥 Premium Videos free", url="https://t.me/+O27nU16V5VszYjg1")],
        [InlineKeyboardButton("🎬 Free Videos", url="https://t.me/+bJy06wHUl79mYWM1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(chat_id=user.id, text=welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    except:
        pass

def main():
    keep_alive() 
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handlers add karna
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(ChatJoinRequestHandler(join_request))
    
    print("Bot is starting...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
