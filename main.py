import telebot
import random
import threading

API_TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
bot = telebot.TeleBot(API_TOKEN)

# لیستی زانیاریەکانی Excel
excel_tips = [
    "Tip 1: Ctrl + Arrow Keys بۆ گواستنەوەی خێرا.",
    "Tip 2: Alt + = بۆ کردنی کۆکردنەوە بەخێرایی.",
    "Tip 3: بەکارهێنانی Conditional Formatting بۆ دیاریکردنی داتای گرنگ.",
    "Tip 4: Freeze Panes بۆ ئەوەی سەرنیشانی خانەکان تەنیشتبن.",
    "Tip 5: VLOOKUP بۆ گەڕان بەناوی خانەکان.",
    "Tip 6: Pivot Tables بۆ چێکردنی راپۆرتەکانی خۆکار.",
    "Tip 7: Flash Fill بۆ تەواوکردنی خانەکان بەخێرایی.",
    "Tip 8: Ctrl + T بۆ گۆڕینی داتا بۆ Table.",
    "Tip 9: IF formula بۆ دروستکردنی ئەندازیارە جیاوازەکان.",
    "Tip 10: CONCATENATE بۆ تێکەڵکردنی نوسین لە خانەکان."
]

# Dictionary بۆ پاراستنی تیپە نێردراوەکان بۆ هەر بەکارهێنەر
sent_tips = {}

# ناردنی زانیاری بە هەموو بەکارهێنەرەکان هەموو ١٢٠ چرکە
def send_tip_every_two_minutes():
    threading.Timer(120, send_tip_every_two_minutes).start()

    for user_id in sent_tips:
        remaining_tips = list(set(excel_tips) - set(sent_tips[user_id]))

        if not remaining_tips:
            bot.send_message(user_id, "تۆ هەموو زانیارییەکان وەرگرتووە. سوپاس!")
            continue

        tip = random.choice(remaining_tips)
        sent_tips[user_id].append(tip)
        bot.send_message(user_id, f"زانیاری نوێی Excel:\n\n{tip}")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in sent_tips:
        sent_tips[user_id] = []
    bot.reply_to(message, "بەخێربێیت! هەر ٢ خۆڵەک جارێک (١٢٠ چرکە) زانیاری نوێی Excel وەردەگری.")

# دەستپێکردنی تایمەر و بۆت
send_tip_every_two_minutes()
bot.infinity_polling()
