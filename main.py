import telebot
from telebot import types
import re
import os
import time
import subprocess
from uuid import uuid4

API_TOKEN = '7595180485:AAELAJ6ZWq2x-S5ruuQzbmSG89zrDqZtvLU'
bot = telebot.TeleBot(API_TOKEN)

user_states = {}
last_download_time = {}

DOWNLOAD_DELAY = 10  # seconds

def is_valid_youtube_link(link):
    return re.match(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/", link)

def is_valid_tiktok_link(link):
    return re.match(r"(https?://)?(www\.)?(tiktok\.com|vt\.tiktok\.com)/", link)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("دابەزاندنی ڤیدیۆ", callback_data="download_video"))
    bot.send_message(message.chat.id, "بەخێربێی بۆ بۆتەکە!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "download_video")
def ask_for_video_link(call):
    user_states[call.from_user.id] = True
    bot.send_message(call.message.chat.id, "❗️ تکایە لینکی ڤیدیۆی یوتوب یاخود تیکتۆک بنێرە تاکو داونلۆدی بکەم")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text

    if user_states.get(user_id, False):
        now = time.time()
        last_time = last_download_time.get(user_id, 0)
        if now - last_time < DOWNLOAD_DELAY:
            remaining = DOWNLOAD_DELAY - int(now - last_time)
            bot.send_message(message.chat.id, f"⏳ تکایە چاوەڕێ بکە {remaining} چرکە پێش ئەوەی دووبارە داونلۆد بکەیت.")
            return

        if is_valid_youtube_link(text):
            download_youtube_video(message)
        elif is_valid_tiktok_link(text):
            download_tiktok_video(message)
        else:
            bot.send_message(message.chat.id, "ببورە لینکەکەت دروست نیە یان قەبارەی ڤیدیۆکە زۆر گەورەیە ❌")
    else:
        bot.send_message(message.chat.id, "تکایە سەرەتا کرتە لە دوگمەی 'دابەزاندنی ڤیدیۆ' بکە.")

def download_youtube_video(message):
    user_id = message.from_user.id
    url = message.text
    file_id = str(uuid4())
    output_path = f"{file_id}.mp4"

    try:
        cmd = [
            "yt-dlp",
            "-f", "mp4",
            "--cookies", "cookies.txt",
            "--ffmpeg-location", "ffmpeg",
            "-o", output_path,
            url
        ]
        subprocess.run(cmd, check=True)

        with open(output_path, 'rb') as f:
            bot.send_video(message.chat.id, f, caption="وێنەیەک بۆتۆو!")

        os.remove(output_path)
        last_download_time[user_id] = time.time()
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "ببورە لینکەکەت دروست نیە یان قەبارەی ڤیدیۆکە زۆر گەورەیە ❌")

def download_tiktok_video(message):
    user_id = message.from_user.id
    url = message.text
    file_id = str(uuid4())
    output_path = f"{file_id}.mp4"

    try:
        cmd = [
            "yt-dlp",
            "-f", "mp4",
            "-o", output_path,
            url
        ]
        subprocess.run(cmd, check=True)

        with open(output_path, 'rb') as f:
            bot.send_video(message.chat.id, f, caption="وێنەیەک بۆتۆو!")

        os.remove(output_path)
        last_download_time[user_id] = time.time()
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "ببورە لینکەکەت دروست نیە یان قەبارەی ڤیدیۆکە زۆر گەورەیە ❌")

bot.infinity_polling()