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
BOT_TOKEN = os.getenv("BOT_TOKEN")  # 🔥 Render ENV
ADMIN_ID = 8293984966  # ← নিজের Telegram ID দাও

CHANNEL_USERNAME = "@all_in_one_63"
GROUP_USERNAME = "@parvezkhan654"

REDEEM_LIMIT = 5

# ================= GIVEAWAY DATA =================
current_code = "GIFT-CHATGPT1246"
current_data = """chat gpt"""

redeemed_users = set()
successful_redeems = 0

# ================= HELPERS =================
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

# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "there"

    text = (
        f"👋 Welcome, {name}!\n\n"
        "This is the Giveaway Management Bot."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)

# ================= Redeem =================
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    join_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{GROUP_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]
    ])

    await query.message.edit_text(
        "Redeem করার আগে Channel ও Group join করো 👇",
        reply_markup=join_keyboard
    )

# ================= Check Join =================
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not await joined_both(context, user_id):
        await query.answer("📌 Please join Channel & Group first", show_alert=True)
        return

    context.user_data.clear()
    context.user_data["awaiting_code"] = True

    await query.message.edit_text("🎟️ Give Your Redeem Code")

# ================= Handle Code =================
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

    # ❌ Wrong Code
    if code != current_code:
        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ])

        await update.message.reply_text(
            "❌ Invalid Code!\n"
            "Please try sending a different code, or cancel.",
            reply_markup=cancel_keyboard
        )
        return

    # ✅ Correct Code
    redeemed_users.add(user_id)
    successful_redeems += 1
    context.user_data.clear()

    redeem_again = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")]
    ])

    await update.message.reply_text(
        f"✅ Redeem successful!\n\n{current_data}",
        reply_markup=redeem_again
    )

# ================= Cancel =================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")]
    ])

    await query.message.edit_text(
        "❌ Cancelled.\n\nআবার Redeem করতে পারো 👇",
        reply_markup=keyboard
    )

# ================= Admin Update =================
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

    app.add_handler(CallbackQueryHandler(redeem, pattern="^redeem$"))
    app.add_handler(CallbackQueryHandler(check_join, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    print("🤖 Giveaway All Bot running on Render")
    app.run_polling()

if __name__ == "__main__":
    main()
