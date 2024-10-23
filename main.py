import telebot
import wikipediaapi
from googletrans import Translator

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'

bot = telebot.TeleBot(API_TOKEN)

# Initialize Wikipedia API and Google Translator
wiki_wiki = wikipediaapi.Wikipedia('en')
translator = Translator()

# Function to handle messages and provide information
@bot.message_handler(func=lambda message: True)
def respond_to_user(message):
    user_query = message.text
    response = get_info(user_query)
    bot.reply_to(message, response)

# Function to fetch information from Wikipedia and translate to Kurdish Sorani
def get_info(query):
    # Fetch the Wikipedia page
    page = wiki_wiki.page(query)
    
    if page.exists():
        summary = page.summary[:1000]  # Limit the summary to 1000 characters
        # Translate the summary to Kurdish Sorani
        translation = translator.translate(summary, src='en', dest='ckb')
        return translation.text
    else:
        return "ببورە، هیچ زانیارییەک نەدۆزرایەوە بەم بابەتەوە."

# Start the bot
bot.polling()