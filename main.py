import telebot
import yt_dlp as youtube_dl
import os

# === Your Telegram Bot Token ===
BOT_TOKEN = '7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI'
bot = telebot.TeleBot(BOT_TOKEN)

# === Make sure 'downloads/' exists ===
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === /start command ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to the YouTube Downloader Bot!\n\n📥 Send me a YouTube link to download the video.")

# === Handle YouTube links ===
@bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be/' in message.text)
def download_youtube_video(message):
    url = message.text
    bot.send_message(message.chat.id, "🔄 Processing your video, please wait...")

    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Decide how to send based on file size
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as video_file:
            if file_size <= 50 * 1024 * 1024:  # 50MB limit for send_video
                bot.send_video(message.chat.id, video_file, caption="✅ Video downloaded successfully!")
            else:
                bot.send_document(message.chat.id, video_file, caption="📦 File is large, sent as a document.")

        os.remove(file_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error:\n{str(e)}")

# === Catch-all for non-links ===
@bot.message_handler(func=lambda message: True)
def handle_non_links(message):
    bot.reply_to(message, "❗ Please send a valid YouTube video link.")

# === Run the bot ===
bot.polling()
