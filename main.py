import telebot
import youtube_dl
import os

# === Your Bot Token ===
BOT_TOKEN = '7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI'
bot = telebot.TeleBot(BOT_TOKEN)

# === Ensure 'downloads/' folder exists ===
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# === /start command ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome!\nSend me a YouTube link and I will download the video for you.")

# === Handle YouTube links ===
@bot.message_handler(func=lambda message: 'youtube.com/watch' in message.text or 'youtu.be/' in message.text)
def download_video(message):
    url = message.text
    bot.reply_to(message, "📥 Downloading... Please wait.")

    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Send the video file
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video)

        os.remove(filename)  # Clean up after sending

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# === Fallback handler ===
@bot.message_handler(func=lambda message: True)
def handle_other(message):
    bot.reply_to(message, "❗ Please send a valid YouTube link.")

# === Run bot ===
bot.polling()
