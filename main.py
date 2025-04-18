from PIL import Image, ImageDraw, ImageFont
import telebot
import random
import threading
import os

API_TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
bot = telebot.TeleBot(API_TOKEN)

excel_tips = [
    "Use Ctrl + Arrow Keys to move faster.",
    "Alt + = for quick sum.",
    "Use conditional formatting.",
    "Freeze panes for visible headers.",
    "VLOOKUP to find data.",
    "Use Flash Fill.",
    "Ctrl + T to make a Table.",
    "Pivot Tables for summaries.",
    "IF function for logic.",
    "Use CONCATENATE or TEXTJOIN."
]

sent_tips = {}

# دروستکردنی وێنەیەکی جوان
def create_image_from_text(tip_text, filename='tip.png'):
    width, height = 1000, 600
    img = Image.new('RGB', (width, height), color=(240, 250, 255))
    draw = ImageDraw.Draw(img)

    # لۆگۆ
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png").resize((100, 100))
        img.paste(logo, (width - 120, 20))

    # فۆنت
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    # ڕاستکردنەوەی نوسین بە ناوەڕاست
    text_w, text_h = draw.textsize(tip_text, font=font)
    x = (width - text_w) // 2
    y = (height - text_h) // 2

    draw.text((x, y), tip_text, font=font, fill=(20, 50, 70))
    img.save(filename)
    return filename

# ناردنی تیپەکە بە شێوەی وێنە
def send_tip_every_120_seconds():
    threading.Timer(120, send_tip_every_120_seconds).start()

    for user_id in sent_tips:
        remaining = list(set(excel_tips) - set(sent_tips[user_id]))
        if not remaining:
            bot.send_message(user_id, "You've received all Excel tips. Thanks!")
            continue
        tip = random.choice(remaining)
        sent_tips[user_id].append(tip)
        image_path = create_image_from_text(tip)
        bot.send_photo(user_id, photo=open(image_path, 'rb'))

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in sent_tips:
        sent_tips[user_id] = []
    bot.reply_to(message, "Welcome! You'll receive a stylish Excel tip image every 2 minutes!")

send_tip_every_120_seconds()
bot.infinity_polling()