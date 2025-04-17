import telebot
import requests

bot = telebot.TeleBot("7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🎵 Send me a TikTok video link to download!")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text)
def download_tiktok(msg):
    url = msg.text.strip()
    api = f"https://tikwm.com/api/?url={url}"
    try:
        res = requests.get(api).json()
        video_url = res['data']['play']
        caption = res['data']['title']
        video = requests.get(video_url)
        with open("tiktok.mp4", "wb") as f:
            f.write(video.content)
        with open("tiktok.mp4", "rb") as f:
            bot.send_video(msg.chat.id, f, caption=caption)
    except:
        bot.reply_to(msg, "❌ Failed to download. Make sure the link is correct and public.")

bot.polling()
