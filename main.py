import telebot
from pytube import YouTube
import os

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_shorts(url):
    try:
        yt = YouTube(url)
        # Get the first mp4 video-only stream (usually Shorts)
        stream = yt.streams.filter(file_extension='mp4', only_video=True).first()
        if stream:
            filepath = stream.download(output_path=DOWNLOAD_FOLDER)
            return filepath
        else:
            return None
    except Exception as e:
        return str(e)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me a YouTube Shorts URL (e.g. https://www.youtube.com/shorts/XXXXXXXXXXX) and I will download the video for you!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "youtube.com/shorts/" not in url:
        bot.reply_to(message, "Please send a valid YouTube Shorts URL (e.g., https://www.youtube.com/shorts/XXXXXXXXXXX)")
        return

    bot.reply_to(message, "Downloading your Shorts video, please wait...")

    result = download_shorts(url)
    if result and os.path.isfile(result):
        with open(result, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)
        os.remove(result)  # Delete after sending
    else:
        bot.reply_to(message, f"Failed to download video: {result}")

bot.polling()
