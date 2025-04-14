import telebot
import requests

# Token بۆ بۆتی تێلێگرامەکەت
BOT_TOKEN = "7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY"

# دروستکردنی بۆت
bot = telebot.TeleBot(BOT_TOKEN)

# API بۆ هەواڵ و زانیاری دراوەکان
CURRENCY_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سڵاو! من بۆتی دراوەکانم. بۆ وەرگرتنی نرخی دراوەکان، 'rate' بنووسە.")

@bot.message_handler(commands=['rate'])
def send_currency_rate(message):
    try:
        response = requests.get(CURRENCY_API_URL)
        data = response.json()
        rates = data.get("rates", {})

        msg = "نرخی نوێترین دراوەکان:\n"
        msg += f"1 USD = {rates.get('EUR', 'N/A')} EUR\n"
        msg += f"1 USD = {rates.get('GBP', 'N/A')} GBP\n"
        msg += f"1 USD = {rates.get('IQD', 'N/A')} IQD\n"

        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, "ببورە، ناتوانم زانیاری وەرگرم.")

# ڕاپەچوو بۆ بۆت
bot.polling()