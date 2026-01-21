import os
import sqlite3
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set this in VPS env variable
CHECK_INTERVAL = 7200  # 2 hours (job check frequency)
JOB_RSS_URL = "https://www.freejobalert.com/rss.xml"  # Example All India job feed
DB_FILE = "users.db"
# ==========================================

# ----- Setup Database -----
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS posts (link TEXT PRIMARY KEY)")
conn.commit()

# ----- Telegram Bot -----
bot = Bot(token=BOT_TOKEN)

# ----- Save User on /start -----
async def start(update, context):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    await update.message.reply_text(
        "✅ Aap registered ho gaye ho.\nAb jitni bhi sarkari job aayegi, sab personal message me milegi 📩"
    )
    print(f"New user registered: {user_id}")

# ----- Get Registered Users -----
def get_users():
    cursor.execute("SELECT id FROM users")
    return [u[0] for u in cursor.fetchall()]

# ----- Send DM to all users -----
def send_dm(message):
    for user_id in get_users():
        try:
            bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")

# ----- Fetch Jobs from RSS -----
def fetch_jobs():
    try:
        r = requests.get(JOB_RSS_URL, timeout=15)
        soup = BeautifulSoup(r.text, "xml")  # XML parser
        items = soup.find_all("item")

        for item in items:
            title = item.title.text
            link = item.link.text

            # Skip if already sent
            cursor.execute("SELECT 1 FROM posts WHERE link=?", (link,))
            if cursor.fetchone():
                continue

            # Save new post
            cursor.execute("INSERT INTO posts (link) VALUES (?)", (link,))
            conn.commit()

            msg = f"""🆕 NEW JOB ALERT

{title}

Official Link 👇
{link}
"""
            send_dm(msg)
            print(f"Sent new job: {title}")

    except Exception as e:
        print("Job fetch error:", e)

# ----- Background Job Loop -----
def job_loop():
    print("🤖 Auto Job Bot Running...")
    while True:
        fetch_jobs()
        time.sleep(CHECK_INTERVAL)

# ----- Run Bot (Telegram Commands + Job Loop) -----
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Run job loop in background thread
    import threading
    job_thread = threading.Thread(target=job_loop, daemon=True)
    job_thread.start()

    print("Bot polling started...")
    app.run_polling()
