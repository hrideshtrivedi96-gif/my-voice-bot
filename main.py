import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Flask - Render ko khush karne ke liye
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    # use_reloader=False bahut zaruri hai warna 2 baar chalega
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# Bot ka kaam
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ON hai! Bolo kya kaam hai?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not client:
        await update.message.reply_text("GROQ key missing hai")
        return
    text = update.message.text
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": text}]
    )
    await update.message.reply_text(resp.choices[0].message.content)

def main():
    # Flask ko background me chalao
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Bot ko main thread me chalao
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Bot starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
