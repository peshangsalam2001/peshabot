import telebot

# Token بۆ بۆتی تێلێگرامەکەت
BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"

# دروستکردنی بۆت
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, " How are you سڵاو بەڕێز پێشەنگ")

bot.remove_webhook()

bot.polling()
