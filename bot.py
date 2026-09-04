import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Flask Server ---
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Bot is active and running!"


def run_flask():
  port = int(os.environ.get("PORT", 5000))
  # use_reloader=False zaroori hai threading ke liye
  app_web.run(host="0.0.0.0", port=port, use_reloader=False)


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
          InlineKeyboardButton("🎁 Redeem Code", callback_data="rede_code"),
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


if __name__ == "__main__":
  # 1. Flask server ko background thread mein start karein
  flask_thread = threading.Thread(target=run_flask, daemon=True)
  flask_thread.start()

  # 2. Telegram Bot ko MAIN thread mein run karein (Error fix ho jayegi)
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  print("Telegram Bot is running smoothly...")
  app.run_polling()
