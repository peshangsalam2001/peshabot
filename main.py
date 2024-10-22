import telebot
import youtube_dl
import os

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

# Create a folder to store downloaded videos
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a YouTube link to download the video in full HD.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    bot.reply_to(message, "Downloading your video... Please wait.")
    
    # Download the video
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', None)
        video_filename = ydl.prepare_filename(info_dict)
    
    # Send the video to the user
    video = open(video_filename, 'rb')
    bot.send_video(message.chat.id, video)
    video.close()

    # Clean up the downloaded file
    os.remove(video_filename)

# Start the bot polling
bot.polling(none_stop=True)