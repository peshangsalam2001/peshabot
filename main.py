import telebot
from telebot import types
import requests
import os
import subprocess
import traceback
import json

API_TOKEN = '7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI'
bot = telebot.TeleBot(API_TOKEN)

CHANNEL_USERNAME = "KurdishBots"
OWNER_ID = 1908245207

DATA_FILE = "user_data.json"

requests.get(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook")

def check_membership(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def add_user(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"downloads": 0}
        save_data(data)

def increment_download(user_id):
    data = load_data()
    if str(user_id) in data:
        data[str(user_id)]["downloads"] += 1
        save_data(data)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not check_membership(message.from_user.id):
        bot.send_message(message.chat.id, "👥 پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت بۆ ئەوەی بتوانیت بۆتەکە بەکاربهێنی \n\n👉 https://t.me/" + CHANNEL_USERNAME)
        return

    add_user(message.from_user.id)

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔗 کەناڵی سەرەکی", url="https://t.me/KurdishBots"),
        types.InlineKeyboardButton("📥 داگرتنی ڤیدیۆ", callback_data="download_prompt"),
        types.InlineKeyboardButton("🎥 چۆنیەتی بەکارهێنان", callback_data="how_to_use"),
        types.InlineKeyboardButton("🧑‍💼 پەیوەندیم پێوە بکە", url="https://t.me/MasterLordBoss")
    )
    bot.send_message(
        message.chat.id,
        "👋 بەخێربێیت بۆ بۆتی داونلۆدکردنی ڤیدیۆی (یوتوب و تیکتۆک)\n\n"
        "🏆 سەردانی کەناڵەکەمان بکە بۆ ئاگاداربون لە نوێترین گۆڕانکاریەکان لە بۆتەکە و سوودمەندبوون لە چەندین بۆتی هاوشێوە\n\n"
        "https://t.me/KurdishBots",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'how_to_use')
def how_to_use(call):
    if not check_membership(call.from_user.id):
        bot.send_message(call.message.chat.id, "👥 تکایە سەرەتا جۆینی کەناڵەکەمان بکە:\n👉 https://t.me/" + CHANNEL_USERNAME)
        return

    video_url = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4"
    bot.send_video(call.message.chat.id, video=video_url, caption="🎥 ڤیدیۆی ڕێنمایی بۆ چۆنیەتی بەکارهێنانی بۆتەکە")

@bot.callback_query_handler(func=lambda call: call.data == 'download_prompt')
def download_instruction(call):
    if not check_membership(call.from_user.id):
        bot.send_message(call.message.chat.id, "👥 پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت \n👉 https://t.me/" + CHANNEL_USERNAME)
        return

    bot.send_message(call.message.chat.id, "☢ تکایە لینکی ڤیدیۆکەت بنێرە بە ڕاست و دروستی تاکو بۆت داونلۆدبکەم")

@bot.message_handler(commands=['stats'])
def send_stats(message):
    if message.from_user.id != OWNER_ID:
        return
    data = load_data()
    total_users = len(data)
    total_downloads = sum(user['downloads'] for user in data.values())
    bot.send_message(message.chat.id, f"📊 زانیارییەکانی بۆت:\n👥 ژمارەی بەکارهێنەران: {total_users}\n📥 ژمارەی داگرتن: {total_downloads}")

@bot.message_handler(commands=['export_users'])
def export_users(message):
    if message.from_user.id != OWNER_ID:
        return
    data = load_data()
    output = "\n".join([f"{user_id}, {info['downloads']}" for user_id, info in data.items()])
    with open("users.txt", "w") as f:
        f.write(output)
    with open("users.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

@bot.message_handler(func=lambda message: True)
def handle_links(message):
    if not check_membership(message.from_user.id):
        bot.send_message(message.chat.id, "👥 پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت \n👉 https://t.me/" + CHANNEL_USERNAME)
        return

    url = message.text.strip()
    if not ("youtube.com" in url or "youtu.be" in url or "tiktok.com" in url):
        bot.reply_to(message, "❌ تکایە دڵنیابەرەوە لە ڕاستی لینکەکە، پاشان لینکەکە بنێرە")
        return

    msg = bot.reply_to(message, "⏳ تکایە چاوەڕوانبە تا بیدیۆکەت بۆ داونلۆدبکەم")

    try:
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]/best",
            "--output", f"{output_dir}/%(title).40s.%(ext)s",
            url
        ]

        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"yt-dlp failed:\n{result.stderr}")

        files = os.listdir(output_dir)
        files.sort(key=lambda x: os.path.getctime(os.path.join(output_dir, x)), reverse=True)
        video_path = os.path.join(output_dir, files[0])
        file_size = os.path.getsize(video_path)

        if file_size > 50 * 1024 * 1024:
            bot.edit_message_text("❗ قەبارەی ڤیدیۆکە زۆر گەورەیە. تکایە لینکێکی تر بنێرە.", message.chat.id, msg.message_id)
            os.remove(video_path)
            return

        with open(video_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="ڤیدیۆکەت بەسەرکەوتوویی داگرت ✅")

        increment_download(message.from_user.id)
        bot.delete_message(message.chat.id, msg.message_id)
        os.remove(video_path)

    except Exception as e:
        bot.edit_message_text(
            f"⚠️ کێشەیەک ڕوویدا:\n\n```{str(e)}```",
            message.chat.id,
            msg.message_id,
            parse_mode="Markdown"
        )

print("Bot is running...")
bot.infinity_polling()