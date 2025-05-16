import telebot
import yt_dlp as youtube_dl
import os

# === Telegram Bot Token ===
BOT_TOKEN = '7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI'
bot = telebot.TeleBot(BOT_TOKEN)

# === Download directory ===
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === /start command ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to the YouTube Downloader Bot!\n\n📥 Send me a YouTube link to download the video.")

# === Handle YouTube link downloads ===
@bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be/' in message.text)
def download_youtube_video(message):
    url = message.text
    bot.send_message(message.chat.id, "🔄 Downloading your video, please wait...")

    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }
        }

        # Use cookies if cookies.txt exists
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as video_file:
            if file_size <= 50 * 1024 * 1024:
                bot.send_video(message.chat.id, video_file, caption="✅ Video downloaded!")
            else:
                bot.send_document(message.chat.id, video_file, caption="📦 Large file sent as document.")

        os.remove(file_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error:\n{str(e)}")

# === Handle other messages ===
@bot.message_handler(func=lambda message: True)
def handle_other(message):
    bot.reply_to(message, "❗ Please send a valid YouTube video link.")

# === Start polling ===
bot.polling()
