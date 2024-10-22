import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

API_KEY = 'YOUR_TELEGRAM_BOT_API_KEY'
bot = telebot.TeleBot(API_KEY)

# Define trivia questions and answers in Kurdish Sorani
quizzes = [
    {
        'question': 'کەی شاری ھەولێر پایتەخت بوو؟',
        'options': ['١٩٢٠', '١٩٣٠', '١٩٤٠', '١٩٥٠'],
        'answer': '١٩٣٠'
    },
    {
        'question': 'بەرزی کوێستانی ھەورامان چەندە؟',
        'options': ['٣٠٠٠م', '٢٤٠٠م', '٢٨٠٠م', '٣٢٠٠م'],
        'answer': '٣٢٠٠م'
    },
    {
        'question': 'بەچێشەکانی کورد لە کێدایە؟',
        'options': ['کورۆن', 'دوپۆن', 'ھەمەکەی', 'بەرپشتی'],
        'answer': 'دوپۆن'
    }
]

current_quiz = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "بەخێربێیت! بۆ دەستپێکردنی کویز /quiz بنووسە.")

@bot.message_handler(commands=['quiz'])
def send_quiz(message):
    global current_quiz
    quiz = random.choice(quizzes)
    current_quiz[message.chat.id] = quiz
    markup = InlineKeyboardMarkup()
    for i, option in enumerate(quiz['options']):
        markup.add(InlineKeyboardButton(text=option, callback_data=f"{i}"))
    bot.send_message(message.chat.id, quiz['question'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global current_quiz
    quiz = current_quiz.get(call.message.chat.id)
    if not quiz:
        bot.send_message(call.message.chat.id, "تکایە یەکەم /quiz بنووسە بۆ دەستپێکردنی کویز.")
        return

    user_answer = int(call.data)
    if quiz['options'][user_answer] == quiz['answer']:
        bot.send_message(call.message.chat.id, "ئەمە ڕاستە! 🥳")
    else:
        bot.send_message(call.message.chat.id, f"ئەمە هەڵەیە. وەڵامی ڕاست: {quiz['answer']}")

bot.polling()