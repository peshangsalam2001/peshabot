import telebot
from tubedl import download

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
        # Download the video using tubedl
        video_path = download(url)
        # Send the video to the user
        with open(video_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, f"Failed to download video: {str(e)}")

bot.polling()