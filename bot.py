import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
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

# User states track karne ke liye dictionary (Jaise Account add karte waqt phone number lena)
user_states = {}


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
  user_id = query.from_user.id

  if data == "start_campaign":
    await query.message.reply_text(
        "🚀 **Mass DM Campaign**\n\nApna campaign shuru karne ke liye pehle"
        " message set karein aur Account add karein. Phir target usernames ki"
        " list bhejiye."
    )

  elif data == "add_account":
    user_states[user_id] = "waiting_for_phone"
    await query.message.reply_text(
        "➕ **Add Account**\n\nKripya apne Telegram account ka **Phone Number**"
        " country code ke sath bhejiye (Jaise: `+919876543210`)."
    )

  elif data == "my_account":
    await query.message.reply_text(
        f"👤 **Account Details**:\n- ID: {user_id}\n- Active Accounts: 0"
    )

  elif data == "how_to_use":
    await query.message.reply_text(
        "📖 **How to Use**:\n1. 'Add Account' par click karke apna account"
        " jodiein.\n2. 'Set Message' se apna text set karein.\n3. 'Start Mass"
        " DM' se campaign run karein."
    )

  elif data == "support":
    await query.message.reply_text(
        "🛠️ Support ke liye admin se contact karein: @Support"
    )

  else:
    await query.message.reply_text(
        f"⚙️ Feature '{data}' par abhi kaam chal raha hai."
    )


# --- Text Message Handler (Phone number / inputs lene ke liye) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  text = update.message.text

  # Check karein ki user account add kar raha hai ya nahi
  if user_states.get(user_id) == "waiting_for_phone":
    user_states[user_id] = None  # State clear karein
    await update.message.reply_text(
        f"✅ Phone number received: `{text}`\n\nAbhi yeh demo mode mein hai,"
        " session string generate karne ke liye API ID aur API Hash ki zaroorat"
        " hoti hai. Jald hi iska full automated setup jud jayega!"
    )
  else:
    await update.message.reply_text(
        "Kripya menu use karne ke liye /start command bhejiye."
    )


if __name__ == "__main__":
  # Flask server background thread mein
  flask_thread = threading.Thread(target=run_flask, daemon=True)
  flask_thread.start()

  # Telegram Bot main thread par
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_handler))
  app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )

  print("Bot is running with Add Account & Mass DM features...")
  app.run_polling()
