import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Logging band taaki error na aaye
logging.getLogger("httpx").setLevel(logging.WARNING)

app = Flask(__name__)
@app.route('/')
def home(): return "Library Wala Bot Live Hai!"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Tera Target / Time System
CONFIG = {"target": 50, "earned": 0, "start": 9, "end": 21}

AI_ROUTER = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768"
]

def get_ai_reply(text):
    for model in AI_ROUTER:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": text}]
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"{model} fail, next try... {e}")
            continue
    return "Sab AI busy hai, 2 min baad try kar."

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Bot ON hai 🔥\nTarget: ${CONFIG['target']}/day\nTime: {CONFIG['start']} to {CONFIG['end']}\n/settarget 100\n/settime 9 21"
    )

async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        CONFIG["target"] = int(context.args[0])
        await update.message.reply_text(f"Target set: ${CONFIG['target']}")
    except:
        await update.message.reply_text("Use: /settarget 50")

async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        CONFIG["start"] = int(context.args[0]); CONFIG["end"] = int(context.args[1])
        await update.message.reply_text(f"Time set: {CONFIG['start']} to {CONFIG['end']}")
    except:
        await update.message.reply_text("Use: /settime 9 21")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Target check
    if CONFIG["earned"] >= CONFIG["target"]:
        await update.message.reply_text(f"🎯 Aaj ka target ${CONFIG['target']} pura! Kal milte hain.")
        return
    
    reply = get_ai_reply(update.message.text)
    CONFIG["earned"] += 1 # har msg pe 1$ demo
    await update.message.reply_text(reply + f"\n\nEarned: ${CONFIG['earned']}/${CONFIG['target']}")

async def voice_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not client: return
    # Voice ko download karke Groq Whisper se text me
    file = await context.bot.get_file(update.message.voice.file_id)
    await file.download_to_drive("voice.ogg")
    with open("voice.ogg", "rb") as f:
        trans = client.audio.transcriptions.create(model="whisper-large-v3", file=f)
    text = trans.text
    await update.message.reply_text(f"Suna: {text}")
    reply = get_ai_reply(text)
    await update.message.reply_text(reply)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False, use_debugger=False)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settarget", set_target))
    application.add_handler(CommandHandler("settime", set_time))
    application.add_handler(MessageHandler(filters.VOICE, voice_handle))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Library wala bot starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
