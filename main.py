import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    CommandHandler,
    ContextTypes
)
from telegram.constants import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")

GROUP_OR_CHANNEL_NAME = "Premium Demo Group"

BUTTON_1_TEXT = "🔥 Premium Videos free"
BUTTON_1_LINK = "https://t.me/+O27nU16V5VszYjg1"

BUTTON_2_TEXT = "🎬 Free Videos"
BUTTON_2_LINK = "https://t.me/+bJy06wHUl79mYWM1"


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    user_id = user.id
    name = user.first_name or "User"

    await update.chat_join_request.approve()

    text = f"""
Hello {name} 👋

✅ Your request to join *{GROUP_OR_CHANNEL_NAME}*
has been *Approved*.
"""

    keyboard = [
        [InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK)],
        [InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK)]
    ]

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(BUTTON_1_TEXT, url=BUTTON_1_LINK)],
        [InlineKeyboardButton(BUTTON_2_TEXT, url=BUTTON_2_LINK)]
    ]

    await update.message.reply_text(
        "👇 Choose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(join_request))
    app.add_handler(CommandHandler("start", start))
    print("Bot started...")
    app.run_polling()
