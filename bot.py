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
  # Ultra-Premium aesthetic layout matching professional panels
  keyboard = [
      [
          InlineKeyboardButton(
              "🚀 ✦ START MASS DM CAMPAIGN ✦ 🚀", callback_data="start_campaign"
          )
      ],
      [
          InlineKeyboardButton(
              "⚡ ✦ FAST Auto-Forward DM ✦ ⚡", callback_data="fast_forward"
          )
      ],
      [
          InlineKeyboardButton("🔍 Scrape Group", callback_data="scrape_group"),
          InlineKeyboardButton("🎁 Invite & Earn", callback_data="invite_earn"),
      ],
      [
          InlineKeyboardButton(
              "💎 VIP Premium Pass", callback_data="vip_premium"
          ),
          InlineKeyboardButton("👤 My Account", callback_data="my_account"),
      ],
      [
          InlineKeyboardButton(
              "➕ Add Session Node", callback_data="add_session"
          ),
          InlineKeyboardButton(
              "❌ Remove Session", callback_data="remove_session"
          ),
      ],
      [
          InlineKeyboardButton(
              "📖 ✦ Tutorial & Terms ✦ 📖", callback_data="tutorial"
          ),
      ],
      [
          InlineKeyboardButton(
              "💬 ✦ Contact Support / Admin ✦ 💬", callback_data="support"
          )
      ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  user = update.effective_user
  welcome_text = (
      f"┏━━━ 🔮 **AUTOMATED DMS PANEL** 🔮 ━━━┓\n\n"
      f"💎 **Enterprise Mass DM & Marketing Engine**\n\n"
      f"✨ Welcome to the most elite Telegram automation suite. "
      f"Engineered with ultra-fast nodes, zero ban security, and "
      f"maximum delivery rates.\n\n"
      f"👤 **Operator:** {user.first_name}\n"
      f"🆔 **Identifier:** `{user.id}`\n"
      f"🟢 **System Status:** 💠 Online & Secure\n\n"
      f"🎁 Claim your complimentary **200 Free DMs** trial now!\n\n"
      f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
      f"⚡ **Powered by:** @SHUBHxSELLER"
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
        "🚀 **Mass DM Campaign Hub**\n\n"
        "⚠️ Please add a working user session first using the 'Add Session"
        " Node' button."
    )
  elif data == "add_session":
    user_states[user_id] = "waiting_for_phone"
    await query.message.reply_text(
        "🔑 **Session Generator Node**\n\n"
        "Please send your Telegram Phone Number with country code.\n"
        "Example: `+919876543210`"
    )
  elif data == "my_account":
    await query.message.reply_text(
        f"👤 **Operator Profile Details**\n\n"
        f"• Account ID: `{user_id}`\n"
        f"• Tier: 💠 Free Trial (200 DMs)\n"
        f"• Active Nodes: 0\n"
        f"• Total Dispatched: 0"
    )
  elif data == "vip_premium":
    await query.message.reply_text(
        "💎 **VIP Elite Subscription Tiers**\n\n"
        "👑 **1 Day Pass:** ₹25\n"
        "👑 **3 Days Pass:** ₹60\n"
        "👑 **7 Days Pass:** ₹120\n"
        "👑 **1 Month Pass:** ₹350\n\n"
        "💬 Instant activation via admin: **@SHUBHxSELLER**"
    )
  elif data == "support":
    await query.message.reply_text(
        "💬 **Dedicated Support Desk**\n\n"
        "For technical assistance or VIP purchases, contact official support:"
        " **@SHUBHxSELLER**"
    )
  else:
    await query.message.reply_text(
        f"⚙️ Module `{data}` is currently locked or under update."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  text = update.message.text

  if user_states.get(user_id) == "waiting_for_phone":
    user_states[user_id] = None
    await update.message.reply_text(
        f"✅ Phone number `{text}` accepted!\n\n"
        "📲 Telegram verification code (OTP) has been dispatched. Please enter"
        " it here."
    )
  else:
    await update.message.reply_text(
        "Please use the interactive control buttons or send /start."
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

  print("Ultra-Premium Bot is running...")
  app.run_polling()
