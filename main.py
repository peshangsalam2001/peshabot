import telebot
import requests

# Replace with your bot token
BOT_TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
bot = telebot.TeleBot(BOT_TOKEN)

# Helper function to download TikTok video via API
def download_tiktok_video(url):
    try:
        # Get video ID
        video_id = requests.get(f"https://api.tikmate.app/api/lookup?url={url}").json().get("token")
        if not video_id:
            return None

        # Get download link
        response = requests.get(f"https://tikmate.online/api/redirect/{video_id}.mp4")
        return response.url
    except Exception as e:
        print("Error:", e)
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send me a TikTok video link, and I'll download it for you!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'tiktok.com' in url:
        bot.send_message(message.chat.id, "Downloading...")
        video_link = download_tiktok_video(url)
        if video_link:
            bot.send_video(message.chat.id, video=video_link)
        else:
            bot.send_message(message.chat.id, "❌ Failed to download. Please try again.")
    else:
        bot.send
