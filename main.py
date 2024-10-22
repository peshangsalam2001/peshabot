import telebot
import pafy
import os

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Welcome! Send me a YouTube link to download the video.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    try:
        video = pafy.new(url)
        best_stream = video.getbest()

        if not best_stream:
            bot.send_message(message.chat.id, "Sorry, no video stream found.")
            return

        video_path = best_stream.download()
        
        # Send the video file to the user
        with open(video_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        # Optionally, remove the video after sending
        os.remove(video_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

# Start polling for messages
bot.polling(none_stop=True)
