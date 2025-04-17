import telebot
from TikTokApi import TikTokApi

bot = telebot.TeleBot("7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سڵاو! لینکی TikTok بنێرە بۆ داونلۆدکردن.")

@bot.message_handler(func=lambda message: True)
def download_tiktok(message):
    url = message.text

    try:
        with TikTokApi() as api:
            video = api.video(url=url)
            video_data = video.bytes()

        with open("video.mp4", "wb") as f:
            f.write(video_data)

        with open("video.mp4", "rb") as video:
            bot.send_video(message.chat.id, video)

    except Exception as e:
        bot.reply_to(message, f"هەڵەیەک ڕوویدا:\n{e}")

bot.polling()
