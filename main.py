import os
import telebot
import yt_dlp

BOT_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'  # Replace with your Telegram bot token

bot = telebot.TeleBot(BOT_TOKEN)

def download_video(url):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = ydl.prepare_filename(info_dict)
        return video_title

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Video Downloader Bot! Send me a video link from any supported platform to download.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    video_url = message.text
    if "http" in video_url:
        bot.reply_to(message, "Fetching the video, please wait...")
        try:
            file_path = download_video(video_url)
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove(file_path)  # Clean up the downloaded file
        except Exception as e:
            bot.reply_to(message, f"Failed to fetch the video. Error: {str(e)}")
    else:
        bot.reply_to(message, "Please send a valid video link.")

bot.infinity_polling()