from telegram.ext import ApplicationBuilder, CommandHandler
import sqlite3

TOKEN = "8519357512:AAETGrN7mTQ67mW1kGIL9F9bVtwqTn_OkUg"

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

async def start(update, context):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    await update.message.reply_text(
        "✅ Aap registered ho gaye ho.\n\nAb jitni bhi sarkari job aayegi, sab personal message me milegi 📩"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
