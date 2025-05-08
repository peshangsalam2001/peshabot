import telebot
import requests

BOT_TOKEN = '7835872937:AAHmy808cQtDdMysSxlli_RlbVKOBkkyApA'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Send me a TikTok video link, and I'll download it for you.")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text)
def download_tiktok_video(message):
    url = message.text.strip()

    api_url = f"https://tikwm.com/api/?url={url}"
    try:
        res = requests.get(api_url).json()
        if res.get("data") and res["data"].get("play"):
            video_url = res["data"]["play"]
            video_response = requests.get(video_url)
            bot.send_video(message.chat.id, video_response.content)
        else:
            bot.send_message(message.chat.id, "❌ Failed to fetch video. Please check the link.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {e}")

bot.polling()
