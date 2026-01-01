import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

print("🔥 V13 GIVEAWAY BOT RUNNING 🔥")

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render ENV
ADMIN_ID = 123456789  # নিজের Telegram ID

CHANNEL_USERNAME = "@your_channel"
GROUP_USERNAME = "@your_group"

REDEEM_LIMIT = 5

# ================= GIVEAWAY DATA =================
current_code = "GIFT-CHATGPT1246"
current_data = """🎁 ChatGPT Plus

Email:
example@email.com

Password:
example123
"""

redeemed_users = set()
successful_redeems = 0

# ================= HELPERS =================
def is_member(bot, chat, user_id):
    try:
        member = bot.get_chat_member(chat, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

def joined_both(bot, user_id):
    return (
        is_member(bot, CHANNEL_USERNAME, user_id)
        and is_member(bot, GROUP_USERNAME, user_id)
    )

# ================= /start =================
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    name = user.first_name or "there"

    text = f"👋 Welcome, {name}!\n\nThis is the Giveaway Management Bot."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")]
    ])

    update.message.reply_text(text, reply_markup=keyboard)

# ================= Redeem =================
def redeem(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{GROUP_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]
    ])

    query.message.edit_text(
        "Redeem করার আগে Channel ও Group join করো 👇",
        reply_markup=keyboard
    )

# ================= Check Join =================
def check_join(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = query.from_user.id

    if not joined_both(context.bot, user_id):
        query.answer("📌 Please join Channel & Group first", show_alert=True)
        return

    context.user_data.clear()
    context.user_data["awaiting_code"] = True
    query.message.edit_text("🎟️ Give Your Redeem Code")

# ================= Handle Code =================
def handle_code(update: Update, context: CallbackContext):
    global successful_redeems

    if not context.user_data.get("awaiting_code"):
        return

    user_id = update.effective_user.id
    code = update.message.text.strip()

    if user_id in redeemed_users:
        update.message.reply_text("⚠️ তুমি আগেই redeem করেছো")
        return

    if successful_redeems >= REDEEM_LIMIT:
        update.message.reply_text("🚫 Giveaway limit শেষ")
        return

    if code != current_code:
        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ])
        update.message.reply_text(
            "❌ Invalid Code!\nTry again or cancel.",
            reply_markup=cancel_keyboard
        )
        return

    redeemed_users.add(user_id)
    successful_redeems += 1
    context.user_data.clear()

    redeem_again = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")]
    ])

    update.message.reply_text(
        f"✅ Redeem successful!\n\n{current_data}",
        reply_markup=redeem_again
    )

# ================= Cancel =================
def cancel(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.user_data.clear()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem")]
    ])

    query.message.edit_text(
        "❌ Cancelled.\n\nআবার Redeem করতে পারো 👇",
        reply_markup=keyboard
    )

# ================= Admin Update =================
def update_code(update: Update, context: CallbackContext):
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

        update.message.reply_text("✅ Giveaway updated successfully.")
    except:
        update.message.reply_text(
            "❌ Format ভুল\n\n/update CODE | Giveaway text"
        )

# ================= MAIN =================
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("update", update_code))

    dp.add_handler(CallbackQueryHandler(redeem, pattern="^redeem$"))
    dp.add_handler(CallbackQueryHandler(check_join, pattern="^check_join$"))
    dp.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_code))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
