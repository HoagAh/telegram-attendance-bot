import os
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
PASSWORD = "28122025"
AUTHORIZED_USERS = set()
attendance_list = []

tz_vietnam = pytz.timezone('Asia/Ho_Chi_Minh')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào mừng! Gõ /hi để điểm danh.")

async def hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.full_name
    now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    time = now.strftime('%H:%M:%S %d/%m/%Y')
    attendance_list.append((user, time))
    await update.message.reply_text(f"{user} đã điểm danh lúc {time}")

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.text == PASSWORD:
        AUTHORIZED_USERS.add(user_id)
        await update.message.reply_text("✅ Xác thực thành công! Bây giờ bạn có thể dùng lệnh /timfile <từ_khóa>")
    else:
        await update.message.reply_text("❌ Mật khẩu sai!")

app = ApplicationBuilder().token("7949088784:AAG0rkhlmIVz_kn1EDreWaFB2Pd6iyoBQJU").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hi", hi))

app.run_polling()
