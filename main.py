import telebot
import youtube_dl

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a Facebook video URL to download.")

@bot.message_handler(func=lambda message: True)
def download_facebook_video(message):
    try:
        url = message.text
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'facebook_video.%(ext)s'
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open('facebook_video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

bot.polling()