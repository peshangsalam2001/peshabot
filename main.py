from PIL import Image, ImageDraw, ImageFont
import telebot
import random
import threading

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

def create_image_from_text(text, filename='tip.png'):
    img = Image.new('RGB', (800, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    d.text((20, 150), text, font=font, fill=(0, 0, 0))
    img.save(filename)
    return filename

def send_tip_every_120_seconds():
    threading.Timer(120, send_tip_every_120_seconds).start()

    for user_id in sent_tips:
        remaining = list(set(excel_tips) - set(sent_tips[user_id]))
        if not remaining:
            bot.send_message(user_id, "You've received all tips!")
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
    bot.reply_to(message, "Welcome! You'll get an Excel tip as an image every 2 minutes.")

send_tip_every_120_seconds()
bot.infinity_polling()