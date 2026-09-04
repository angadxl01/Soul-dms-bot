import os
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# --- Flask Server (Render free tier ko active rakhne ke liye) ---
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Bot is active and running!"


# --- Telegram Bot Code ---
TOKEN = "8627528321:AAFSSdgHID0Mizwhx5hxulhIa-CErWR5Yu0"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [
      [
          InlineKeyboardButton(
              "🚀 Start Mass DM Campaign", callback_data="start_campaign"
          )
      ],
      [
          InlineKeyboardButton("✉️ Set Message", callback_data="set_message"),
          InlineKeyboardButton(
              "👁️ Preview Message", callback_data="preview_message"
          ),
      ],
      [
          InlineKeyboardButton("👤 My Account", callback_data="my_account"),
          InlineKeyboardButton(
              "👑 Go VIP Premium", callback_data="go_vip_premium"
          ),
      ],
      [
          InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem_code"),
          InlineKeyboardButton("➕ Add Account", callback_data="add_account"),
      ],
      [
          InlineKeyboardButton(
              "➖ Remove Account", callback_data="remove_account"
          ),
          InlineKeyboardButton(
              "👥 Join Request DM", callback_data="join_request_dm"
          ),
      ],
      [
          InlineKeyboardButton("📖 How to Use", callback_data="how_to_use"),
          InlineKeyboardButton("🛠️ Support", callback_data="support"),
      ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  user = update.effective_user
  await update.message.reply_text(
      f"🆔 Your ID: {user.id}\n👤 Username: @{user.username}\n\n👇 Choose an"
      " option below:",
      reply_markup=reply_markup,
  )


def run_bot():
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  print("Bot is running...")
  app.run_polling()


if __name__ == "__main__":
  import threading

  # Bot ko background thread mein chalayein
  t = threading.Thread(target=run_bot)
  t.start()

  # Flask server ko port par run karein (Render ke liye zaruri hai)
  port = int(os.environ.get("PORT", 5000))
  app_web.run(host="0.0.0.0", port=port)
