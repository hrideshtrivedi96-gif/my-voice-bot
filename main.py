import os
from telegram.ext import Application, MessageHandler, filters
from telegram import Update

async def start(update: Update, context):
    await update.message.reply_text("Boss bot ON hai! Voice bhejo.")

# Yaha se full voice bot code start hoga
# (Maine pura code short kar diya hai deploy ke liye)

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, start))
app.run_polling()
