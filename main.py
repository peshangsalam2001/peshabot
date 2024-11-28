import telebot
import requests

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
        # Using Safeform.net API to download the video
        response = requests.get(f'https://safeform.net/api/video/download?url={video_url}')
        response.raise_for_status()
        
        # Assuming the API returns a direct download link
        download_link = response.json()['download_link']

        # Sending the video file back to the user
        bot.send_message(message.chat.id, "Here is your download link:")
        bot.send_message(message.chat.id, download_link)
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

bot.infinity_polling()