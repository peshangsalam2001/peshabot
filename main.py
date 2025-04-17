import telebot
import requests
from telebot import types

bot = telebot.TeleBot("7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🎵 Send me a TikTok video link to download! You can choose the resolution after.")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text)
def get_video_info(msg):
    url = msg.text.strip()
    api = f"https://tikwm.com/api/?url={url}"
    try:
        res = requests.get(api).json()
        video_title = res['data']['title']
        video_id = res['data']['id']
        resolutions = res['data']['quality']
        
        # Create inline keyboard with resolution options
        markup = types.InlineKeyboardMarkup()
        for resolution in resolutions:
            button = types.InlineKeyboardButton(f"{resolution['label']}", callback_data=f"download_{video_id}_{resolution['quality']}")
            markup.add(button)
        
        bot.send_message(msg.chat.id, f"Select resolution for '{video_title}':", reply_markup=markup)
    except Exception as e:
        bot.reply_to(msg, f"❌ Failed to fetch video info. Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('download_'))
def download_video(call):
    try:
        _, video_id, quality = call.data.split('_')
        api = f"https://tikwm.com/api/?url=https://www.tiktok.com/{video_id}"
        res = requests.get(api).json()
        video_url = next(quality_data['play'] for quality_data in res['data']['quality'] if quality_data['quality'] == quality)
        
        # Download video
        video = requests.get(video_url)
        with open("tiktok.mp4", "wb") as f:
            f.write(video.content)
        
        # Send video
        with open("tiktok.mp4", "rb") as f:
            bot.send_video(call.message.chat.id, f)
        bot.answer_callback_query(call.id, "Video is ready to download!")
    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Error occurred while downloading.")
        print(e)

bot.polling()
