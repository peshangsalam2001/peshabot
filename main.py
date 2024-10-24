import telebot
from videoget import VideoGet

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token
BOT_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me a YouTube URL to download the video.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    try:
        # Download the video using videoget
        video = VideoGet(url)
        video.download()
        # Get the downloaded video file path
        video_path = video.get_filepath()

        # Send the video to the user
        with open(video_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        # Optionally, delete the file after sending
        import os
        os.remove(video_path)
    except Exception as e:
        bot.reply_to(message, f"Failed to download video: {str(e)}")

bot.polling()