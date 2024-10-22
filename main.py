Text to Speech (gtts)

import telebot
from gtts import gTTS
import os

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me any text and I'll convert it to speech in Kurdish.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    tts = gTTS(text=text, lang='ku')
    tts.save('output.mp3')
    
    with open('output.mp3', 'rb') as audio:
        bot.send_voice(message.chat.id, audio)
    
    os.remove('output.mp3')

bot.polling()