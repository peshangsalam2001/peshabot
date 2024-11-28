import telebot
from keepvid import KeepVid

# Replace with your own API token
API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a YouTube link and I'll download the video for you.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    video_url = message.text
    bot.reply_to(message, "Downloading video...")

    try:
        # Using KeepVid to download the video
        keepvid = KeepVid()
        video = keepvid.get(video_url)
        stream = video.streams.get_highest_resolution()

        # Download the video file
        stream.download()

        # Send the video file to the user
        video_file_path = stream.get_file_path()
        with open(video_file_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

bot.infinity_polling()