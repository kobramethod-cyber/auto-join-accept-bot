from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# ===== BOT TOKEN (tumhara) =====
BOT_TOKEN = "8151979678:AAHonAeiyFTgoKeZqok3OTG5Rc4jnVJRZYs"

# ===== BUTTON TEXT =====
BUTTON_1_TEXT = "🔥 Premium Videos free"
BUTTON_2_TEXT = "🎬 Free Videos"

# ===== BUTTON LINKS =====
BUTTON_1_LINK = "https://t.me/+O27nU16V5VszYjg1"
BUTTON_2_LINK = "https://t.me/+bJy06wHUl79mYWM1"

# ===== MESSAGE TEXT =====
WELCOME_TEXT = (
    "✅ **Request Accepted!**\n\n"
    "Neeche buttons se free content dekho 👇"
)

# ===== JOIN REQUEST HANDLER =====
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user

    # Accept request
    await update.chat_join_request.approve()

    # Buttons
    keyboard = [
        [InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK)],
        [InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send private message
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=WELCOME_TEXT,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except:
        pass  # user ne DM band kiya ho to crash na ho

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(join_request))
    app.run_polling()

if __name__ == "__main__":
    main()
