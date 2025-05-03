import telebot
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def reply_with_site_answer(message):
    user_question = message.text
    try:
        # ئەم نموونەیە GET بەکار دەهێنێت بۆ وێبسایتەکەت، پێویستە ئەم URL و پارامەتەرەکان بگۆڕیت بەپێی وێبسایتەکەت
        response = requests.get(f"https://zaniary.com/search?q={user_question}")
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # وەرگرتنی ناوەڕۆکی div بە کلاسی js_blog_content
        answer_div = soup.find('div', class_='js_blog_content')
        if answer_div:
            # پاککردنی تاقیەکان و تەنها نوسینەکە وەرگرە
            answer_text = answer_div.get_text(strip=True)
            if answer_text:
                bot.reply_to(message, answer_text)
            else:
                bot.reply_to(message, "ببورە، وەڵام نەدۆزرایەوە.")
        else:
            bot.reply_to(message, "ببورە، وەڵام نەدۆزرایەوە.")
    except Exception as e:
        bot.reply_to(message, f"کێشە هەیە لە وەرگرتنی وەڵام: {e}")

bot.polling()
