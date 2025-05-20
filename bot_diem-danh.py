import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
attendance_list = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào mừng! Gõ /hi để điểm danh.")

async def hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.full_name
    time = datetime.now().strftime('%H:%M:%S %d/%m/%Y')
    attendance_list.append((user, time))
    await update.message.reply_text(f"{user} đã điểm danh lúc {time}")

app = ApplicationBuilder().token("7949088784:AAG0rkhlmIVz_kn1EDreWaFB2Pd6iyoBQJU").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hi", hi))

app.run_polling()
