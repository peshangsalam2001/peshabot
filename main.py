import telebot
import yt_dlp
import requests
import time

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'

bot = telebot.TeleBot(API_TOKEN)

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': '/tmp/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        video_filename = ydl.prepare_filename(info_dict)
        return video_filename

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me a video URL from Facebook, TikTok, Instagram, or Snapchat, and I'll download it for you!")

@bot.message_handler(func=lambda message: True)
def download_and_send_video(message):
    url = message.text
    try:
        video_file = download_video(url)
        with open(video_file, 'rb') as video:
            bot.send_video(message.chat.id, video)
        bot.send_message(message.chat.id, "Here is your video!")
    except Exception as e:
        bot.reply_to(message, "Sorry, I couldn't download the video. Please try again.")
    time.sleep(5)  # Add a delay to prevent spamming

bot.polling()