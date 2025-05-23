import os
import pytz
import requests
import random
import openai
from openai import OpenAI
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# ======= Cấu hình =======
BOT_TOKEN = "7886971109:AAHU2IY4Guf0VdjBNGw-wjD_Rm1UTwdJrEA"
YOUTUBE_API_KEY = "AIzaSyD3lYq0iiYKJlN63oMaVcIsAnaQlwPfSaI"
OPENAI_API_KEY = "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"
CORRECT_PASSWORD = "28122025"
AUTHORIZED_USERS = set()
attendance_list = []
openai.api_key = OPENAI_API_KEY

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
    await update.message.reply_text(f"📌 {attendance}\n🔐 Vui lòng nhập mật khẩu để truy cập tài liệu.\n Nhập /timvideo để tìm video bạn muốn.\n❗ Nhập nội dung sau lệnh /chat để hỏi ChatGPT.")

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

def search_youtube(query, max_results=5):
    url = "https://www.googleapis.com/youtube/v3/search"
    today = datetime.utcnow().isoformat("T") + "Z"  # thời gian hiện tại (UTC)
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "relevance",  # hoặc "date"
        "key": YOUTUBE_API_KEY,
        "maxResults": 50  # lấy nhiều hơn rồi chọn ngẫu nhiên
    }
    response = requests.get(url, params=params)
    data = response.json()

    videos = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        link = f"https://www.youtube.com/watch?v={video_id}"
        videos.append((title, link))

    random.shuffle(videos)
    return videos[:max_results]

async def timvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Bạn cần nhập từ khóa. Ví dụ: /timvideo python cơ bản")
        return

    query = " ".join(context.args)
    videos = search_youtube(query)

    if not videos:
        await update.message.reply_text("❌ Không tìm thấy video phù hợp.")
        return

    reply = f"🔎 Kết quả tìm kiếm cho: *{query}*\n\n"
    for i, (title, link) in enumerate(videos, start=1):
        reply += f"{i}. [{title}]({link})\n"

    await update.message.reply_text(reply, parse_mode="Markdown")

# ==== 🤖 CHATGPT ====
async def chat_with_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❗ Nhập nội dung sau lệnh /chat để hỏi ChatGPT.")
        return

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}]
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)


# ======= Khởi động bot =======
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hi", hi))
app.add_handler(CommandHandler("chat", chat_with_gpt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))
app.add_handler(CommandHandler("timvideo", timvideo))

app.run_polling()
