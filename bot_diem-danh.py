import os
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# ======= Cấu hình =======
BOT_TOKEN = "7949088784:AAG0rkhlmIVz_kn1EDreWaFB2Pd6iyoBQJU"
CORRECT_PASSWORD = "28122025"
AUTHORIZED_USERS = set()
attendance_list = []

GOOGLE_DRIVE_LINKS = [
    ("Hóa học", "https://drive.google.com/drive/folders/1R1mnaaW4SQE8RCC0s7aCNIUqziwu2Rt0?usp=drive_link"),
    ("Vật Lý", "https://drive.google.com/drive/folders/1ZjPYD6GyQtknLWgJ4HUEhs0yYDZMJuF1?usp=drive_link"),
    ("Toán", "https://drive.google.com/drive/folders/1IuzMQM-HspXdi6eV_Jcke_DFCGfyvwFP?usp=drive_link"),
]

tz_vietnam = pytz.timezone('Asia/Ho_Chi_Minh')

# ======= Lệnh /start =======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Chào mừng! Gõ /hi để điểm danh.")

# ======= Lệnh /hi để điểm danh =======
async def hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    now = datetime.now(tz_vietnam).strftime("%H:%M:%S - %d/%m/%Y")
    attendance = f"{user.full_name} đã điểm danh lúc {now}"
    attendance_list.append(attendance)
    await update.message.reply_text(f"📌 {attendance}\n🔐 Vui lòng nhập mật khẩu để truy cập tài liệu.")

# ======= Xử lý mật khẩu =======
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text == CORRECT_PASSWORD:
        AUTHORIZED_USERS.add(user_id)

        reply = "✅ Xác thực thành công!\n📂 Danh sách link Google Drive:\n\n"
        for idx, (title, link) in enumerate(GOOGLE_DRIVE_LINKS, start=1):
            reply += f"{idx}. [{title}]({link})\n"
        await update.message.reply_text(reply, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Mật khẩu không đúng. Thử lại.")

# ======= Khởi động bot =======
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hi", hi))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))

app.run_polling()
