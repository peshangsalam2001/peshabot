import telebot
import yt_dlp
import os
import time
from threading import Lock

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Dictionary to store last download timestamp per user
user_last_download_time = {}
lock = Lock()
COOLDOWN_SECONDS = 30  # User must wait 30 seconds between downloads

def download_shorts_yt_dlp(url):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Send me a YouTube Shorts URL (e.g., https://www.youtube.com/shorts/XXXXXXXXXXX) "
        "and I will download the video for you!\n"
        "Please wait 30 seconds between each download request."
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    url = message.text.strip()

    if "youtube.com/shorts/" not in url:
        bot.reply_to(message, "Please send a valid YouTube Shorts URL (e.g., https://www.youtube.com/shorts/XXXXXXXXXXX)")
        return

    with lock:
        last_time = user_last_download_time.get(user_id, 0)
        elapsed = time.time() - last_time
        if elapsed < COOLDOWN_SECONDS:
            wait_time = int(COOLDOWN_SECONDS - elapsed)
            bot.reply_to(message, f"⏳ Please wait {wait_time} seconds before sending a new link.")
            return
        # Update last download time to current time
        user_last_download_time[user_id] = time.time()

    bot.reply_to(message, "Downloading your Shorts video, please wait...")

    try:
        filepath = download_shorts_yt_dlp(url)
        with open(filepath, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)
        os.remove(filepath)
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to download video: {e}")

bot.polling()
