import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8293984966

CHANNEL_USERNAME = "@all_in_one_63"
GROUP_USERNAME = "@parvezkhan654"

REDEEM_LIMIT = 5

current_code = "GIFT-CHATGPT1246"
current_data = "chat gpt"

redeemed_users = set()
successful_redeems = 0


async def is_member(context, chat, user_id):
    try:
        member = await context.bot.get_chat_member(chat, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False


async def joined_both(context, user_id):
    return (
        await is_member(context, CHANNEL_USERNAME, user_id)
        and await is_member(context, GROUP_USERNAME, user_id)
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")]]
    )
    await update.message.reply_text(
        "👋 Welcome!\n\nThis is the Giveaway Management Bot.",
        reply_markup=keyboard,
    )


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{GROUP_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]
    ])

    await query.message.edit_text(
        "Redeem করার আগে Channel ও Group join করো 👇",
        reply_markup=keyboard
    )


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not await joined_both(context, user_id):
        await query.answer("আগে join করো", show_alert=True)
        return

    context.user_data["awaiting_code"] = True
    await query.message.edit_text("🎟️ Give Your Redeem Code")


async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_redeems

    if not context.user_data.get("awaiting_code"):
        return

    user_id = update.effective_user.id
    code = update.message.text.strip()

    if user_id in redeemed_users:
        await update.message.reply_text("⚠️ তুমি আগেই redeem করেছো")
        return

    if successful_redeems >= REDEEM_LIMIT:
        await update.message.reply_text("🚫 Giveaway limit শেষ")
        return

    if code != current_code:
        await update.message.reply_text("❌ Invalid Code")
        return

    redeemed_users.add(user_id)
    successful_redeems += 1
    context.user_data.clear()

    await update.message.reply_text(
        f"✅ Redeem successful!\n\n{current_data}"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(redeem, pattern="^redeem$"))
    app.add_handler(CallbackQueryHandler(check_join, pattern="^check_join$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    print("🤖 Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
