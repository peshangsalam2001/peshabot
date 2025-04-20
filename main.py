import telebot

# زانیارییە بنەڕەتییەکان
TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
CHANNEL_LINK = 'https://t.me/PeshangTestChannel'
ADMIN_CHAT_ID = 1908245207

bot = telebot.TeleBot(TOKEN)

# بۆ تۆمارکردنی ئەوەی تۆ کلیکت کردووە یان نا
has_clicked = False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    join_button = telebot.types.InlineKeyboardButton("چۆینبکە", url=CHANNEL_LINK, callback_data='joined')
    markup.add(join_button)

    bot.send_photo(
        message.chat.id,
        photo='https://imgur.com/a/2EDWQ0H',  # گۆڕە بە لینکی وێنە
        caption="تکایە جۆینی ئەم چەناڵە بکەن",
        reply_markup=markup
    )

    bot.send_message(message.chat.id, f"IDی تۆ: {message.chat.id}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    global has_clicked
    if call.data == 'joined' and call.from_user.id == ADMIN_CHAT_ID:
        if not has_clicked:
            has_clicked = True
            bot.send_message(ADMIN_CHAT_ID, "پیرۆزە! تۆ کلیکی دوگمەکە کردووە.")
        else:
            bot.answer_callback_query(call.id, "تۆ پێشتر کلیکت کردووە.")
    elif call.from_user.id != ADMIN_CHAT_ID:
        bot.answer_callback_query(call.id, "تەنها خاونی بۆت دەتوانێ کلیک بکات.")

# دەستپێکردنی بۆت
bot.polling()