import requests
import time
import sqlite3
from bs4 import BeautifulSoup
from telegram import Bot

# ========= CONFIG =========
BOT_TOKEN = "8519357512:AAETGrN7mTQ67mW1kGIL9F9bVtwqTn_OkUg"
CHECK_INTERVAL = 7200  # 2 hours
# ==========================

bot = Bot(token=BOT_TOKEN)

# Database setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS posts (link TEXT PRIMARY KEY)")
conn.commit()

# -------- Save user --------
def save_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

# -------- Get users --------
def get_users():
    cursor.execute("SELECT id FROM users")
    return [u[0] for u in cursor.fetchall()]

# -------- Send DM --------
def send_dm(message):
    for user_id in get_users():
        try:
            bot.send_message(chat_id=user_id, text=message)
        except:
            pass

# -------- Job Source (SAFE PUBLIC SITE) --------
def fetch_jobs():
    url = "https://www.freejobalert.com/rss.xml"
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "xml")
    items = soup.find_all("item")

    for item in items:
        title = item.title.text
        link = item.link.text

        cursor.execute("SELECT 1 FROM posts WHERE link=?", (link,))
        if cursor.fetchone():
            continue

        cursor.execute("INSERT INTO posts (link) VALUES (?)", (link,))
        conn.commit()

        msg = f"""🆕 NEW JOB ALERT

{title}

Official Link 👇
{link}
"""
        send_dm(msg)

# -------- MAIN LOOP --------
print("🤖 Personal Auto Job Bot Running...")
while True:
    try:
        fetch_jobs()
    except Exception as e:
        print("Error:", e)

    time.sleep(CHECK_INTERVAL)
