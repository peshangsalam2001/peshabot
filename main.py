import telebot
from pytube import YouTube
import os

# Replace with your bot token
BOT_TOKEN = '7780162828:AAEryLvBrK82X0jjNFfyU4GCiSEqHYzZ1js'
bot = telebot.TeleBot(BOT_TOKEN)

# Create a downloads directory if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Send me a YouTube link and I’ll download the video in the highest quality.")

@bot.message_handler(func=lambda m: True)
def download_youtube_video(message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "❌ Please send a valid YouTube link.")
        return

    msg = bot.reply_to(message, "📥 Downloading your video... Please wait.")
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        file_path = stream.download(output_path='downloads')
        
        file_size = os.path.getsize(file_path)
        if file_size >= 50 * 1024 * 1024:
            bot.send_message(message.chat.id, "⚠️ The video is larger than 50MB and cannot be sent through Telegram.")
        else:
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption=f"🎬 {yt.title}")

        os.remove(file_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ An error occurred:\n{str(e)}")

bot.polling()
