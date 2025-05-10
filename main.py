import telebot
from telebot import types
import subprocess
import os
import re
import random
import time

API_TOKEN = '7595180485:AAELAJ6ZWq2x-S5ruuQzbmSG89zrDqZtvLU'
bot = telebot.TeleBot(API_TOKEN)

user_states = {}

def is_youtube_url(url):
    return 'youtu.be' in url or 'youtube.com' in url

def is_tiktok_url(url):
    return 'tiktok.com' in url

def download_video_with_limit(url, max_size_mb=50):
    formats = ['bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
               '18',  # 360p
               '22',  # 720p
               '17']  # lower fallback

    for fmt in formats:
        filename = f"video_{random.randint(1000, 9999)}.mp4"
        command = [
            "yt-dlp",
            "-f", fmt,
            "-o", filename,
            "--cookies", "cookies.txt",
            "--no-playlist",
            url
        ]

        try:
            subprocess.run(command, check=True)
            if os.path.exists(filename) and os.path.getsize(filename) <= max_size_mb * 1024 * 1024:
                return filename
            else:
                if os.path.exists(filename):
                    os.remove(filename)
        except subprocess.CalledProcessError:
            continue

    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("دابەزاندنی ڤیدیۆ")
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        "بەخێربێیت بۆ بۆتی دابەزاندنی ڤیدیۆ!\n\nتکایە دوگمەی خوارەوە بکەرەوە:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "دابەزاندنی ڤیدیۆ")
def request_link(message):
    user_states[message.chat.id] = True
    bot.send_message(
        message.chat.id,
        "❗️ تکایە لینکی ڤیدیۆی یوتوب یاخود تیکتۆک بنێرە تاکو داونلۆدی بکەم"
    )

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_links(message):
    if user_states.get(message.chat.id):
        url = message.text.strip()

        if is_youtube_url(url) or is_tiktok_url(url):
            msg = bot.reply_to(message, "چاوەڕێ بکە...")
            time.sleep(random.randint(5, 10))

            filename = download_video_with_limit(url)

            if filename and os.path.exists(filename):
                with open(filename, 'rb') as video:
                    bot.send_video(
                        message.chat.id,
                        video,
                        caption="بەسەرکەوتویی دابەزاندرا ✅"
                    )
                os.remove(filename)
            else:
                bot.send_message(
                    message.chat.id,
                    "ببورە لینکەکەت دروست نیە یان قەبارەی ڤیدیۆکە زۆر گەورەیە ❌"
                )
        else:
            bot.send_message(
                message.chat.id,
                "ببورە لینکەکەت دروست نیە یان قەبارەی ڤیدیۆکە زۆر گەورەیە ❌"
            )
    else:
        bot.send_message(
            message.chat.id,
            "تکایە سەرەتا دوگمەی \"دابەزاندنی ڤیدیۆ\" بکەرەوە."
        )

bot.infinity_polling()