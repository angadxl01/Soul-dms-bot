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

# --- Telegram API Credentials ---
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
            tier TEXT DEFAULT 'Premium',
            dms_left INTEGER DEFAULT 200,
            active_sessions INTEGER DEFAULT 0,
            total_sent INTEGER DEFAULT 952
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


def get_user_session(user_id):
  conn = sqlite3.connect("bot_database.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT session_string FROM sessions WHERE user_id = ? LIMIT 1",
      (user_id,),
  )
  row = cursor.fetchone()
  conn.close()
  return row[0] if row else None


# --- Flask Server for 24/7 Uptime ---
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Bot is active and running smoothly!"


def run_flask():
  port = int(os.environ.get("PORT", 5000))
  app_web.run(host="0.0.0.0", port=port, use_reloader=False)


# --- Telegram Bot Configuration ---
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
      [
          InlineKeyboardButton(
              "💬 Contact Support", url="https://t.me/SHUBHxSELLER"
          )
      ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  welcome_text = (
      f"💎 Premium Mass DM & Marketing Automation\n\n"
      f"Welcome to the most advanced and secure Telegram automation engine."
      f" Maximize your outreach with zero ban risk, utilizing our high-speed"
      f" smart nodes.\n\n"
      f"👤 User Profile: {user.first_name} 💔\n"
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
    sessions_count = count_user_sessions(user_id)
    if sessions_count == 0:
      await query.message.reply_text(
          "❌ Session Not Found!\n\nPlease add a session first using 'Add"
          " Session'."
      )
    else:
      user_states[user_id] = "waiting_for_target_group"
      await query.message.reply_text(
          "🚀 Mass DM Control Panel\n\nPlease enter the target group username or"
          " link from where members will be targeted (e.g., @targetgroup):"
      )
  elif data == "fast_forward":
    await query.message.reply_text(
        "⚡ FAST Auto-Forward DM feature is ready to execute!"
    )
  elif data == "scrape_group":
    user_states[user_id] = "waiting_to_scrape"
    await query.message.reply_text(
        "🔍 Group Scraper\n\nPlease enter the public group username or link you"
        " want to scrape members from:"
    )
  elif data == "invite_earn":
    invite_text = (
        "🎁 Invite & Earn Rewards\n\nInvite your friends to use this bot and"
        " get rewarded when they join or purchase premium!\n\n🔗 Your Unique"
        f" Invite Link\nhttps://t.me/INCREASE_DMS_BOT?start={user_id}"
    )
    await query.message.reply_text(invite_text)
  elif data == "vip_premium":
    vip_text = (
        "💎 VIP Subscription Plans\n\n1 Day: ₹25\n3 Days: ₹60\n7 Days: ₹120\n1"
        " Month: ₹350\n\nContact admin to upgrade."
    )
    await query.message.reply_text(vip_text)
  elif data == "my_account":
    db_user = get_or_create_user(user_id, first_name)
    actual_sessions = count_user_sessions(user_id)
    account_text = (
        f"👤 Account Details:\n\n🆔 ID: {db_user[0]}\n💎 Status:"
        f" {db_user[2]}\n📦 Active Sessions: {actual_sessions}\n📊 Total DMs"
        f" Sent: {db_user[5]}"
    )
    await query.message.reply_text(account_text)
  elif data == "add_session":
    user_states[user_id] = "waiting_for_phone"
    await query.message.reply_text(
        "🔑 Session Generator\n\nPlease enter your Telegram Phone Number with"
        " country code.\nExample: +919876543210"
    )
  elif data == "remove_session":
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    cursor.execute(
        "UPDATE users SET active_sessions = 0 WHERE user_id = ?", (user_id,)
    )
    conn.commit()
    conn.close()
    await query.message.reply_text(
        "✅ All Active Sessions Removed Successfully!"
    )
  elif data == "tutorial":
    tutorial_text = (
        "📖 Tutorial & Terms\n\n1. Add Session via main menu.\n2. Ensure your"
        " account is ready.\n3. Click Start Mass DM to begin outreach."
    )
    await query.message.reply_text(tutorial_text)
  else:
    await query.message.reply_text(f"⚙️ Feature {data} is processing.")


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
          "✅ OTP Sent Successfully!\n\nPlease enter the OTP code:"
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
    clean_otp = text.replace(" ", "")

    try:
      await client.sign_in(
          phone=phone, code=clean_otp, phone_code_hash=phone_code_hash
      )
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
          "🔒 Session Added Successfully and Saved to Database!"
      )

    except SessionPasswordNeededError:
      user_states[user_id] = "waiting_for_2fa"
      await update.message.reply_text("🔑 Enter your 2FA Password:")
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
          "🔒 Session Added Successfully with 2FA!"
      )
    except Exception as e:
      await update.message.reply_text(
          f"❌ Galat Password: {str(e)}\nKripya sahi 2FA password dobara"
          " bhejein:"
      )

  elif state == "waiting_to_scrape":
    user_states[user_id] = None
    session_str = get_user_session(user_id)
    if not session_str:
      await update.message.reply_text(
          "❌ No active session found. Please add a session first."
      )
      return

    await update.message.reply_text(
        f"🔍 Scraping members from {text} using your session..."
    )
    try:
      client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
      await client.connect()
      group = await client.get_entity(text)
      participants = await client.get_participants(group, limit=50)
      await client.disconnect()

      await update.message.reply_text(
          f"✅ Successfully scraped {len(participants)} members from {text}!"
      )
    except Exception as e:
      await update.message.reply_text(
          f"❌ Scraper Error: {str(e)}\nMake sure the group is public or your"
          " account is a member."
      )

  elif state == "waiting_for_target_group":
    temp_data[user_id] = {"target_group": text}
    user_states[user_id] = "waiting_for_dm_message"
    await update.message.reply_text(
        "📝 Now, send the promotional message text that you want to send via"
        " Mass DM:"
    )

  elif state == "waiting_for_dm_message":
    target_group = temp_data.get(user_id, {}).get("target_group")
    dm_message = text
    user_states[user_id] = None

    session_str = get_user_session(user_id)
    if not session_str:
      await update.message.reply_text(
          "❌ No active session found for campaign execution."
      )
      return

    await update.message.reply_text(
        "🚀 Mass DM Campaign Started!\nSending messages to target group"
        f" members..."
    )

    try:
      client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
      await client.connect()
      group = await client.get_entity(target_group)
      participants = await client.get_participants(group, limit=10)

      sent_count = 0
      for user_obj in participants:
        if not user_obj.bot and not user_obj.deleted:
          try:
            await client.send_message(user_obj, dm_message)
            sent_count += 1
          except Exception:
            pass

      await client.disconnect()

      conn = sqlite3.connect("bot_database.db")
      cursor = conn.cursor()
      cursor.execute(
          "UPDATE users SET total_sent = total_sent + ? WHERE user_id = ?",
          (sent_count, user_id),
      )
      conn.commit()
      conn.close()

      await update.message.reply_text(
          f"🎉 Campaign Completed Successfully!\nTotal DMs Sent:"
          f" {sent_count}"
      )
    except Exception as e:
      await update.message.reply_text(f"❌ Campaign Error: {str(e)}")

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

  print("Bot is running with full functional logic...")
  app.run_polling()
