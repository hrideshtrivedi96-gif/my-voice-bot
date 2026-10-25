import os
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Alive! Library Wala Fix Hai."

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def start_bot():
    if not BOT_TOKEN or not GROQ_API_KEY:
        print("ERROR: BOT_TOKEN ya GROQ_API_KEY missing hai Render me!")
        return
    try:
        from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
        from telegram import Update
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("Bot ON hai 🔥 502 fix ho gaya!")

        async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":update.message.text}])
            await update.message.reply_text(resp.choices[0].message.content)

        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
        print("Bot polling start...")
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Bot crash error: {e}")

# Bot ko background me daalo, Flask ko main me rakho
threading.Thread(target=start_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)
