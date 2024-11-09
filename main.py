import telebot
from googletrans import Translator

# Initialize the bot and translator
bot_token = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(bot_token)
translator = Translator()

@bot.message_handler(func=lambda message: True)
def translate_message(message):
    # Translate the incoming message from Kurdish to English
    translated = translator.translate(message.text, src='ku', dest='en')
    # Send the translated text back to the user
    bot.send_message(message.chat.id, translated.text)

# Start polling for messages
bot.polling()