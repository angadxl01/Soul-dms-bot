import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# --- Flask Server ---
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Bot is active and running!"


def run_flask():
  port = int(os.environ.get("PORT", 5000))
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


# --- Button Click Handlers ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  data = query.data

  if data == "start_campaign":
    await query.message.reply_text(
        "🚀 Mass DM Campaign feature par kaam chal raha hai. Jald hi yeh active"
        " hoga!"
    )
  elif data == "set_message":
    await query.message.reply_text(
        "✉️ Apni message yahan set karne ke liye text bhejiye."
    )
  elif data == "preview_message":
    await query.message.reply_text(
        "👁️ Aapne abhi tak koi message set nahi kiya hai."
    )
  elif data == "my_account":
    user = query.from_user
    await query.message.reply_text(
        f"👤 **Account Details**:\n- ID: {user.id}\n- Plan: Free\n- Accounts"
        " Added: 0"
    )
  elif data == "go_vip_premium":
    await query.message.reply_text(
        "👑 VIP Premium lene ke liye admin se संपर्क (contact) karein."
    )
  elif data == "redeem_code":
    await query.message.reply_text(
        "🎁 Apna redeem code yahan bhejiye (e.g., /redeem YOUR_CODE)."
    )
  elif data == "add_account":
    await query.message.reply_text(
        "➕ Naya account add karne ke liye session string ya phone number"
        " dein."
    )
  elif data == "remove_account":
    await query.message.reply_text(
        "➖ Remove karne ke liye koi account available nahi hai."
    )
  elif data == "join_request_dm":
    await query.message.reply_text(
        "👥 Join Request DM feature enable/disable karne ke liye option"
        " chuniye."
    )
  elif data == "how_to_use":
    await query.message.reply_text(
        "📖 **How to Use**:\n1. Pehle account add karein.\n2. Phir message set"
        " karein.\n3. Mass DM campaign start karein!"
    )
  elif data == "support":
    await query.message.reply_text(
        "🛠️ Kisi bhi madad ke liye support team se contact karein: @Support"
    )


if __name__ == "__main__":
  # Flask server ko background thread mein start karein
  flask_thread = threading.Thread(target=run_flask, daemon=True)
  flask_thread.start()

  # Telegram Bot ko main thread par run karein
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_handler))

  print("Telegram Bot with features is running smoothly...")
  app.run_polling()
