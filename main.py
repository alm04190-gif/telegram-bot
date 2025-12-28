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

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8293984966

CHANNEL_USERNAME = "@parvezkhan_00"
GROUP_USERNAME = "@parvezkhan_654"

REDEEM_LIMIT = 5

# ================= GIVEAWAY DATA =================
current_code = "GIFT-CHATGPT1246"
current_data = """ChatGPT Plus

Email:
example@email.com

Password:
example123
"""

redeemed_users = set()
successful_redeems = 0

# ================= HELPERS =================
async def is_member(context, chat, user_id):
    try:
        m = await context.bot.get_chat_member(chat, user_id)
        return m.status in ("member", "administrator", "creator")
    except:
        return False

async def joined_both(context, user_id):
    return (
        await is_member(context, CHANNEL_USERNAME, user_id)
        and await is_member(context, GROUP_USERNAME, user_id)
    )

# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        await update.message.reply_text(
            "👑 Admin Mode\n\n/update CODE | Giveaway text"
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{GROUP_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
    ])

    await update.message.reply_text(
        "Giveaway নিতে হলে আগে Channel ও Group join করো:",
        reply_markup=keyboard
    )

# ================= CHECK JOIN =================
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not await joined_both(context, user_id):
        await query.answer("❌ আগে Channel ও Group join করো", show_alert=True)
        return

    await query.message.edit_text(
        "🎁 Ready to redeem!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")]
        ])
    )

# ================= ASK CODE =================
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data["awaiting_redeem"] = True
    await query.message.reply_text("👉 Redeem code পাঠাও:")

# ================= USER REDEEM =================
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_redeems

    if not context.user_data.get("awaiting_redeem"):
        return

    user_id = update.effective_user.id
    code = update.message.text.strip()

    if not await joined_both(context, user_id):
        await update.message.reply_text("❌ Please join channel & group first")
        return

    if user_id in redeemed_users:
        await update.message.reply_text("⚠️ তুমি আগেই redeem করেছো")
        return

    if successful_redeems >= REDEEM_LIMIT and user_id != ADMIN_ID:
        await update.message.reply_text("🚫 Giveaway limit শেষ")
        return

    if code != current_code:
        await update.message.reply_text("❌ Invalid redeem code")
        return

    redeemed_users.add(user_id)
    if user_id != ADMIN_ID:
        successful_redeems += 1

    context.user_data.clear()
    await update.message.reply_text(f"✅ Redeem successful!\n\n{current_data}")

# ================= ADMIN UPDATE =================
async def update_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_code, current_data, redeemed_users, successful_redeems

    if update.effective_user.id != ADMIN_ID:
        return

    try:
        _, payload = update.message.text.split(" ", 1)
        code, text = payload.split("|", 1)

        current_code = code.strip()
        current_data = text.strip()

        redeemed_users.clear()
        successful_redeems = 0

        await update.message.reply_text("✅ Giveaway updated successfully.")
    except:
        await update.message.reply_text(
            "❌ Format ভুল\n\n/update CODE | Giveaway text"
        )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("update", update_code))
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    app.add_handler(CallbackQueryHandler(redeem, pattern="redeem"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    print("🤖 Bot running (stable)")
    app.run_polling()

if __name__ == "__main__":
    main()
