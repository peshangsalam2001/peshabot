import telebot
from pytube import YouTube
import os

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
API_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Welcome! Send me a YouTube link to download the video.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    try:
        yt = YouTube(url)
        # Get the highest resolution stream (preferably Full HD)
        video_stream = yt.streams.filter(res="1080p", file_extension='mp4').first() or yt.streams.get_highest_resolution()

        if not video_stream:
            bot.send_message(message.chat.id, "Sorry, no 1080p video stream found.")
            return

        video_path = video_stream.download()
        
        # Send the video file to the user
        with open(video_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        # Optionally, remove the video after sending
        os.remove(video_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

# Start polling for messages
bot.polling(none_stop=True)
