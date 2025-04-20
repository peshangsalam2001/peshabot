import telebot
import json
import os

# زانیاری بنەڕەتی
TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
CHANNEL_LINK = 'https://t.me/PeshangTestChannel'
ADMIN_CHAT_ID = 1908245207  # IDی تۆ لێرە دانێ (دەتوانیت بە /start بۆتەکە لە دواتر چاپی بکەیت)

bot = telebot.TeleBot(TOKEN)

# دروستکردنی فایلەکە ئەگەر بوونی نەبوو
if not os.path.exists('data.json'):
    with open('data.json', 'w') as file:
        json.dump({"clicked_users": []}, file)

# بارکردنی داتا
def load_data():
    with open('data.json', 'r') as file:
        return json.load(file)

# هەڵگرتنی نوێکردنەوە
def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file)

# فرمانی /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    join_button = telebot.types.InlineKeyboardButton("چۆینبکە", url=CHANNEL_LINK, callback_data='joined')
    markup.add(join_button)

    bot.send_photo(
        message.chat.id,
        photo='https://example.com/image.jpg',  # لینکێکی وێنە لێرە دانێ
        caption="تکایە جۆینی ئەم چەناڵە بکەن",
        reply_markup=markup
    )

    # نیشاندانی ID بۆ دۆزینەوە
    bot.send_message(message.chat.id, f"IDی تۆ: {message.chat.id}")

# هەڵسەنگاندنی کلیک
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'joined':
        user_id = call.from_user.id
        data = load_data()

        if user_id not in data['clicked_users']:
            data['clicked_users'].append(user_id)
            save_data(data)

            total = len(data['clicked_users'])
            if total == 2:  # لە 2 کلیک
                bot.send_message(ADMIN_CHAT_ID, "پیرۆزە! ٢ بەکارهێنەر کلیکیان کرد و جۆینیان کردووە.")
        else:
            bot.answer_callback_query(call.id, "تۆ پێشتر کلیکت کردووە.")

# دەستپێکردنی بۆتەکە
bot.polling()