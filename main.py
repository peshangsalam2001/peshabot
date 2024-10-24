import telebot
import requests

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a Facebook reel URL to download.")

@bot.message_handler(func=lambda message: True)
def download_facebook_reel(message):
    try:
        url = message.text
        api_url = f"https://fdownloader.net/api/facebook?url={url}"
        response = requests.get(api_url).json()
        video_url = response['video_url']
        video_content = requests.get(video_url).content
        with open('facebook_reel.mp4', 'wb') as video_file:
            video_file.write(video_content)
        with open('facebook_reel.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

bot.polling()