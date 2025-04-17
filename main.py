import telebot
import requests

BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"
bot = telebot.TeleBot(BOT_TOKEN)

# Function to get download link from Instagram
def download_instagram_video(insta_url):
    try:
        api_url = "https://saveig.app/api/ajaxSearch"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        }
        data = {"q": insta_url}
        res = requests.post(api_url, headers=headers, data=data)

        video_url = res.json()["data"][0]["url"]
        return video_url
    except Exception as e:
        print("Error:", e)
        return None

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Send me an Instagram post or reel link, and I'll download it for you!")

@bot.message_handler(func=lambda message: True)
def handle_links(message):
    url = message.text
    if "instagram.com" in url:
        bot.send_message(message.chat.id, "⏳ Getting download link...")
        video_url = download_instagram_video(url)
        if video_url:
            bot.send_video(message.chat.id, video=video_url)
        else:
            bot.send_message(message.chat.id, "❌ Failed to get video. Make sure the link is public.")
    else:
        bot.send_message(message.chat.id, "Please send a valid Instagram link.")

bot.polling()
