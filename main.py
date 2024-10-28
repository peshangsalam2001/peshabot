import telebot
import requests

bot_token = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Send the Instagram video URL to download.")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    video_url = message.text
    api_url = "https://snapvideo.io/api/ajaxSearch"  # Placeholder URL if SnapVideo provides a public API endpoint
    response = requests.post(api_url, data={"url": video_url}).json()

    download_link = response.get("download_link")  # Adjust based on actual API response structure
    if download_link:
        bot.send_message(message.chat.id, download_link)
    else:
        bot.send_message(message.chat.id, "Video not found or an error occurred.")

bot.polling()