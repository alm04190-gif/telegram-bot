import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8293984966

CHANNEL_USERNAME = "@parvezkhan_00"
GROUP_USERNAME = "@parvezkhan_654"

REDEEM_LIMIT = 5

current_code = "GIFT-CHATGPT1246"
current_data = """ChatGPT Plus

Email:
example@email.com

Password:
example123
"""

redeemed_users = set()
successful_redeems = 0

# ---------------- Flask ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---------------- Helpers ----------------
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

# ---------------- Bot ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Mode\n\n/update CODE | Giveaway text")
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

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not await joined_both(context, q.from_user.id):
        await q.answer("❌ আগে join করো", show_alert=True)
        return

    await q.message.edit_text(
        "🎁 Ready!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Redeem", callback_data="redeem")]
        ])
    )

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["redeem"] = True
    await q.message.reply_text("Redeem code পাঠাও:")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global successful_redeems

    if not context.user_data.get("redeem"):
        return

    user_id = update.effective_user.id
    code = update.message.text.strip()

    if user_id in redeemed_users:
        await update.message.reply_text("⚠️ Already redeemed")
        return

    if code != current_code:
        await update.message.reply_text("❌ Wrong code")
        return

    redeemed_users.add(user_id)
    successful_redeems += 1
    context.user_data.clear()

    await update.message.reply_text(f"✅ Success!\n\n{current_data}")

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

        await update.message.reply_text("✅ Updated")
    except:
        await update.message.reply_text("❌ /update CODE | text")

# ---------------- Main ----------------
def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("update", update_code))
    app_bot.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    app_bot.add_handler(CallbackQueryHandler(redeem, pattern="redeem"))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    app_bot.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
