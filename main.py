import telebot

TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
CHANNEL_LINK = 'https://t.me/PeshangTestChannel'
ADMIN_CHAT_ID = 1908245207

bot = telebot.TeleBot(TOKEN)

# لیستی بەکارهێنەرانی کلیک‌کردو، لە یاداشتە ناوخۆیی
clicked_users = set()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    join_button = telebot.types.InlineKeyboardButton("چۆینبکە", url=CHANNEL_LINK, callback_data='joined')
    markup.add(join_button)

    bot.send_photo(
        message.chat.id,
        photo='https://example.com/image.jpg',  # گۆڕە بە لینکێکی وێنە
        caption="تکایە جۆینی ئەم چەناڵە بکەن",
        reply_markup=markup
    )

    # نیشاندانی ID بۆ تۆ
    bot.send_message(message.chat.id, f"IDی تۆ: {message.chat.id}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'joined':
        user_id = call.from_user.id

        if user_id not in clicked_users:
            clicked_users.add(user_id)

            if len(clicked_users) == 2:  # گەیشتن بە ٢ کلیک
                bot.send_message(ADMIN_CHAT_ID, "پیرۆزە! ٢ بەکارهێنەر کلیکیان کرد و جۆینیان کردووە.")
        else:
            bot.answer_callback_query(call.id, "تۆ پێشتر کلیکت کردووە.")

# دەستپێکردنی بۆت
bot.polling()