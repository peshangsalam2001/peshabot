import telebot
import yt_dlp
import os

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "بەخێربێن بۆ بۆتی داونلۆدکردنی ڤیدیۆی تیکتۆک، تکایە لینکی ڤیدیۆکە بنێرە و چاوەڕوانبە بۆ ئەوەی بە بەرزترین کوالیتی داونلۆدیکەین.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text

    # Check if the URL contains 'tiktok.com'
    if 'tiktok.com' not in url:
        bot.send_message(message.chat.id, "تکایە لینکی دروست بنێرە.")
        return

    try:
        ydl_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'video')
            video_file = f"{video_title}.mp4"

        # Send the video file to the user
        with open(video_file, 'rb') as video_file_handle:
            bot.send_video(message.chat.id, video_file_handle)

        # Optionally, remove the video after sending
        os.remove(video_file)

    except Exception as e:
        bot.send_message(message.chat.id, f"ببورە پڕۆسەکە سەرکەوتوو نەبوو: {str(e)}")

# Start polling for messages
bot.polling(none_stop=True)
