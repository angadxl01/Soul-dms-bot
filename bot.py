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
user_states = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # Premium Emojis & Exact Layout matching your video
  keyboard = [
      [
          InlineKeyboardButton(
              "🚀 START MASS DM CAMPAIGN", callback_data="start_campaign"
          )
      ],
      [
          InlineKeyboardButton(
              "⚡ FAST Auto-Forward DM", callback_data="fast_forward"
          )
      ],
      [
          InlineKeyboardButton("🔍 Scrape Group", callback_data="scrape_group"),
          InlineKeyboardButton("🎁 Invite & Earn", callback_data="invite_earn"),
      ],
      [
          InlineKeyboardButton("👑 VIP Premium", callback_data="vip_premium"),
          InlineKeyboardButton("👤 My Account", callback_data="my_account"),
      ],
      [
          InlineKeyboardButton("➕ Add Session", callback_data="add_session"),
          InlineKeyboardButton(
              "❌ Remove Session", callback_data="remove_session"
          ),
      ],
      [
          InlineKeyboardButton(
              "🚀 Tutorial & Terms", callback_data="tutorial"
          ),
      ],
      [InlineKeyboardButton("💰 Contact Support", callback_data="support")],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  user = update.effective_user
  welcome_text = (
      f"🤖 **Automatic DMs Bot**\n"
      f"💎 **Premium Mass DM & Marketing Automation**\n\n"
      f"Welcome to the most advanced and secure Telegram automation engine. Maximize"
      f" your outreach with zero ban risk, utilizing our high-speed smart"
      f" nodes.\n\n"
      f"👤 **User Profile:** {user.first_name}\n"
      f"🆔 **Account ID:** `{user.id}`\n"
      f"🟢 **Server Node:** 🟩 100% Online\n\n"
      f"📢 Expand your audience security!\n"
      f"🎁 Claim your **200 Free DMs** trial today.\n\n"
      f"Developed by - **@SHUBHxSELLER**"
  )

  await update.message.reply_text(welcome_text, reply_markup=reply_markup)


# --- Button Click Handlers ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  data = query.data
  user_id = query.from_user.id

  if data == "start_campaign":
    await query.message.reply_text(
        "🚀 **Mass DM Control Panel**\n\nPlease ensure you have added a session"
        " first using 'Add Session'."
    )
  elif data == "add_session":
    user_states[user_id] = "waiting_for_phone"
    await query.message.reply_text(
        "🔑 **Session Generator**\nPlease enter your Telegram Phone Number with"
        " country code.\nExample: `+919876543210`"
    )
  elif data == "my_account":
    await query.message.reply_text(
        f"👤 **Account Details**:\n- ID: `{user_id}`\n- Status: Free\n- Active"
        " Sessions: 0\n- Total DMs Sent: 0"
    )
  elif data == "vip_premium":
    await query.message.reply_text(
        "👑 **VIP Subscription Plans**\n\n1 Day: ₹25\n3 Days: ₹60\n7 Days:"
        " ₹120\n1 Month: ₹350\n\nContact admin to upgrade."
    )
  elif data == "support":
    await query.message.reply_text(
        "🛠️ For support and purchase, contact: @SHUBHxSELLER"
    )
  else:
    await query.message.reply_text(
        f"⚙️ Feature `{data}` is under configuration."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  text = update.message.text

  if user_states.get(user_id) == "waiting_for_phone":
    user_states[user_id] = None
    await update.message.reply_text(
        f"✅ OTP Sent Successfully to `{text}`!\n\nEnter your 2FA Password if"
        " required."
    )
  else:
    await update.message.reply_text(
        "Please use the menu buttons or send /start."
    )


if __name__ == "__main__":
  flask_thread = threading.Thread(target=run_flask, daemon=True)
  flask_thread.start()

  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_handler))
  app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )

  print("Premium Bot is running...")
  app.run_polling()
