Workout Bot (Kurdish Vc)

import telebot
import random
from datetime import datetime, timedelta
from gtts import gTTS
import os

API_KEY = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_KEY)

# Define workout routines and fitness tips in Kurdish Sorani
workouts = [
    {"routine": "چەندین جەستەی ئامادەکردن", "tips": "بە شێوەیەکی ڕاست بنچینەکانت بەکاربەرە."},
    {"routine": "دوو وەرزشی شەوی بەرز", "tips": "بەرزکردنەوەی وەرزشی شەوی پێویستە بەرز بکەیت."},
    {"routine": "هەفتەی یەکەمی پەیچ", "tips": "سەرەتای پەیچ لە زنجیرەی پەیچی دابنێ."},
    {"routine": "کەوتن و ڕووبەڕو", "tips": "چەندین کەوتنی خوارەوە بۆ پەیچ بەرز بکە."},
    {"routine": "تایبەتمەندی چەندین وەرزشی گرتن", "tips": "هەر بەرز بوونی سەرەوە ڕوونە."}
]

last_sent = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "بەخێربێیت! بۆ وەرگرتنی ڕووتینی ورزشی ڕۆژانە، /daily بنووسە.")

@bot.message_handler(commands=['daily'])
def send_daily(message):
    global last_sent
    chat_id = message.chat.id
    now = datetime.now()
    
    if chat_id in last_sent and now - last_sent[chat_id] < timedelta(days=1):
        bot.reply_to(message, "تکایە چاوەڕوانی بکە بۆ ڕووتینی پێشوو.")
    else:
        workout = random.choice(workouts)
        bot.send_message(chat_id, f"ڕووتینی ڕۆژ: **{workout['routine']}**")

        # Generate audio file from the tip
        tts = gTTS(text=workout['tips'], lang='ckb')  # 'ckb' is the language code for Kurdish
        audio_file = 'tip.mp3'
        tts.save(audio_file)

        # Send the audio file
        with open(audio_file, 'rb') as audio:
            bot.send_voice(chat_id, audio)

        # Cleanup the audio file
        os.remove(audio_file)

        last_sent[chat_id] = now

bot.polling()