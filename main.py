import telebot
import yt_dlp
import os

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

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
    bot.reply_to(message, "Send me a YouTube Shorts URL and I will download the video for you!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "youtube.com/shorts/" not in url:
        bot.reply_to(message, "Please send a valid YouTube Shorts URL (e.g., https://www.youtube.com/shorts/XXXXXXXXXXX)")
        return

    bot.reply_to(message, "Downloading your Shorts video, please wait...")

    try:
        filepath = download_shorts_yt_dlp(url)
        with open(filepath, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)
        os.remove(filepath)
    except Exception as e:
        bot.reply_to(message, f"Failed to download video: {e}")

bot.polling()
