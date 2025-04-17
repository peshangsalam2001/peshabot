import os
import telebot
from tiktok_scraper import TikTokScraper
from tiktok_scraper.utils import download_file

BOT_TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'  # Replace with your Telegram bot token

bot = telebot.TeleBot(BOT_TOKEN)
scraper = TikTokScraper()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to TikTok Downloader Bot! Send me a TikTok video link to download.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    video_url = message.text
    if "tiktok.com" in video_url:
        bot.reply_to(message, "Fetching the video, please wait...")
        try:
            video_info = scraper.get_video_info(video_url)
            video_download_url = video_info['video_url']
            file_path = download_file(video_download_url, directory="downloads", filename="video.mp4")
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove(file_path)  # Clean up the downloaded file
        except Exception as e:
            bot.reply_to(message, f"Failed to fetch the video. Error: {str(e)}")
    else:
        bot.reply_to(message, "Please send a valid TikTok video link.")

bot.infinity_polling()
    else:
        bot.send_message(message.chat.id, "Please send a valid Instagram link.")

bot.polling()
