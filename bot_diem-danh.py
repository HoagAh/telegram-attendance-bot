import os
import pytz
import requests
import random
from openai import OpenAI
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# ======= Cấu hình =======

BOT_TOKEN = "7886971109:AAHU2IY4Guf0VdjBNGw-wjD_Rm1UTwdJrEA"
YOUTUBE_API_KEY = "AIzaSyD3lYq0iiYKJlN63oMaVcIsAnaQlwPfSaI"
CORRECT_PASSWORD = "28122025"

token = os.environ["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"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

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


# ==== ChatGPT =====
async def chat_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text("❗ Nhập \chat để trò chuyện với AI\n Ví dụ: \gpt hello?", parse_mode="Markdown")
        return

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "What is the capital of France?",
                }
            ],
            temperature=1.0,
            top_p=1.0,
            model=model
        )
        
        print(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"⚠️Không thể gọi AI: {str(e)}")


# ======= Khởi động bot =======
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hi", hi))
app.add_handler(CommandHandler("gpt", chat_gpt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))
app.add_handler(CommandHandler("timvideo", timvideo))

app.run_polling()
