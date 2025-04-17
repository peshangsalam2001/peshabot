import telebot
from telebot import types
import json
import os

# بۆت تۆکنت لێرە دابنێ
TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'

# دروستکردنی بۆت
bot = telebot.TeleBot(TOKEN)

# فایلی کۆرسەکان
COURSES_FILE = 'courses.json'

# ئەگەر فایلی کۆرسەکان بوونی نەبوو، دروستی بکە بە نموونەی سەرەتایی
if not os.path.exists(COURSES_FILE):
    default_courses = {
        "categories": [
            {
                "id": 1,
                "name": "پرۆگرامینگ",
                "courses": [
                    {
                        "id": 101,
                        "title": "فێربوونی پایثۆن",
                        "description": "کۆرسێکی سەرەتایی بۆ فێربوونی زمانی پایثۆن",
                        "price": "١٠٠،٠٠٠ دینار",
                        "image_url": "https://example.com/python.jpg",
                        "duration": "٨ هەفتە"
                    },
                    {
                        "id": 102,
                        "title": "جاڤاسکریپت",
                        "description": "فێربوونی جاڤاسکریپت بۆ گەشەپێدانی وێب",
                        "price": "١٢٠،٠٠٠ دینار",
                        "image_url": "https://example.com/javascript.jpg",
                        "duration": "١٠ هەفتە"
                    }
                ]
            },
            {
                "id": 2,
                "name": "زمان",
                "courses": [
                    {
                        "id": 201,
                        "title": "زمانی ئینگلیزی",
                        "description": "کۆرسی پێشکەوتووی زمانی ئینگلیزی",
                        "price": "٨٠،٠٠٠ دینار",
                        "image_url": "https://example.com/english.jpg",
                        "duration": "١٢ هەفتە"
                    }
                ]
            }
        ]
    }
    
    with open(COURSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_courses, f, ensure_ascii=False, indent=4)

# خوێندنەوەی زانیاری کۆرسەکان
def load_courses():
    with open(COURSES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# فەرمانی سەرەتا
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # دوگمەکانی سەرەکی
    courses_btn = types.KeyboardButton("📚 کۆرسەکان")
    about_btn = types.KeyboardButton("ℹ️ دەربارەی ئێمە")
    contact_btn = types.KeyboardButton("📞 پەیوەندی")
    register_btn = types.KeyboardButton("📝 تۆمارکردن")
    
    markup.add(courses_btn, about_btn, contact_btn, register_btn)
    
    bot.send_message(
        message.chat.id,
        f"سڵاو {message.from_user.first_name}! 👋\n\n"
        "بەخێربێیت بۆ بۆتی کۆرسەکانمان.\n"
        "دەتوانیت لێرەوە سەیری کۆرسەکانمان بکەیت و زانیاری وەربگریت.",
        reply_markup=markup
    )

# هەڵگرتنی داواکاریەکانی بەکارهێنەر
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text == "📚 کۆرسەکان":
        show_categories(message)
    elif message.text == "ℹ️ دەربارەی ئێمە":
        show_about(message)
    elif message.text == "📞 پەیوەندی":
        show_contact(message)
    elif message.text == "📝 تۆمارکردن":
        show_registration(message)
    elif message.text == "🔙 گەڕانەوە بۆ سەرەتا":
        send_welcome(message)
    else:
        # بەدواداچوون بکە بزانە ئایا بەکارهێنەر کرتەی لەسەر هیچ پۆلێنێک کردووە
        courses_data = load_courses()
        for category in courses_data["categories"]:
            if message.text == f"🔍 {category['name']}":
                show_courses_in_category(message, category)
                return
        
        # بەدواداچوون بکە بزانە ئایا بەکارهێنەر کرتەی لەسەر هیچ کۆرسێک کردووە
        for category in courses_data["categories"]:
            for course in category["courses"]:
                if message.text == f"📖 {course['title']}":
                    show_course_details(message, course)
                    return
        
        # ئەگەر پەیامەکە نەناسرایەوە
        bot.reply_to(message, "ببورە، نەمتوانی تێبگەم.
تکایە یەکێک لە بژاردەکان هەڵبژێرە.")

# نیشاندانی پۆلێنەکان
def show_categories(message):
    courses_data = load_courses()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = []
    for category in courses_data["categories"]:
        buttons.append(types.KeyboardButton(f"🔍 {category['name']}"))
    
    buttons.append(types.KeyboardButton("🔙 گەڕانەوە بۆ سەرەتا"))
    markup.add(*buttons)
    
    bot.send_message(
        message.chat.id,
        "تکایە پۆلێنێک هەڵبژێرە:",
        reply_markup=markup
    )

# نیشاندانی کۆرسەکانی ناو پۆلێنێک
def show_courses_in_category(message, category):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = []
    for course in category["courses"]:
        buttons.append(types.KeyboardButton(f"📖 {course['title']}"))
    
    buttons.append(types.KeyboardButton("🔙 گەڕانەوە بۆ سەرەتا"))
    markup.add(*buttons)
    
    bot.send_message(
        message.chat.id,
        f"کۆرسەکانی پۆلێنی {category['name']}:",
        reply_markup=markup
    )

# نیشاندانی وردەکاری کۆرسێک
def show_course_details(message, course):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    register_btn = types.KeyboardButton("📝 تۆمارکردن")
    back_btn = types.KeyboardButton("🔙 گەڕانەوە بۆ سەرەتا")
    markup.add(register_btn, back_btn)
    
    # ئامادەکردنی زانیاری کۆرس
    course_info = f"*{course['title']}*\n\n"
    course_info += f"📋 *شیکردنەوە:* {course['description']}\n"
    course_info += f"💰 *نرخ:* {course['price']}\n"
    course_info += f"⏱ *ماوە:* {course['duration']}\n"
    
    # ناردنی وێنەی کۆرس ئەگەر هەبوو
    if 'image_url' in course and course['image_url']:
        try:
            bot.send_photo(
                message.chat.id,
                course['image_url'],
                caption=course_info,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            # ئەگەر نەتوانرا وێنەکە بنێردرێت، تەنها تێکستەکە دەنێردرێت
            bot.send_message(
                message.chat.id,
                course_info,
                parse_mode='Markdown',
                reply_markup=markup
            )
    else:
        # ئەگەر وێنە نەبوو
        bot.send_message(
            message.chat.id,
            course_info,
            parse_mode='Markdown',
            reply_markup=markup
        )

# نیشاندانی دەربارەی ئێمە
def show_about(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    back_btn = types.KeyboardButton("🔙 گەڕانەوە بۆ سەرەتا")
    markup.add(back_btn)
    
    about_text = (
        "*دەربارەی ئێمە*\n\n"
        "ئێمە خزمەتگوزاری فێرکاری پێشکەش دەکەین لە بوارە جیاوازەکاندا. "
        "مامۆستایانی بە ئەزموون و پرۆگرامی تایبەت ئامادەکراون بۆ یارمەتیدانت "
        "لە گەیشتن بە ئامانجەکانت.\n\n"
        "تیمەکەمان بەردەوام کار لەسەر نوێکردنەوەی کۆرسەکان دەکات بۆ دڵنیابوون "
        "لە پێشکەشکردنی باشترین ناوەڕۆک و مەنهەج."
    )
    
    bot.send_message(
        message.chat.id,
        about_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

# نیشاندانی پەیوەندی
def show_contact(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    back_btn = types.KeyboardButton("🔙 گەڕانەوە بۆ سەرەتا")
    markup.add(back_btn)
    
    contact_text = (
        "*پەیوەندی کردن*\n\n"
        "📱 *ژمارەی تەلەفۆن:* +964 750 123 4567\n"
        "✉️ *ئیمەیل:* info@example.com\n"
        "🌐 *ماڵپەڕ:* www.example.com\n"
        "📍 *ناونیشان:* شەقامی سەرەکی، سلێمانی، هەرێمی کوردستان\n\n"
        "کاتەکانی کارکردن:\n"
        "شەممە - پێنجشەممە: ١٠:٠٠ - ١٧:٠٠"
    )
    
    bot.send_message(
        message.chat.id,
        contact_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

# نیشاندانی فۆرمی تۆمارکردن
def show_registration(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    back_btn = types.KeyboardButton("🔙 گەڕانەوە بۆ سەرەتا")
    markup.add(back_btn)
registration_text = (
        "*تۆمارکردن بۆ کۆرسەکان*\n\n"
        "بۆ تۆمارکردن لە هەر کۆرسێک، تکایە ئەم زانیاریانە بنێرە بۆ ئیمەیلی register@example.com:\n\n"
        "1️⃣ ناوی تەواو\n"
        "2️⃣ ژمارەی تەلەفۆن\n"
        "3️⃣ ئیمەیل\n"
        "4️⃣ ناوی کۆرسی دڵخواز\n\n"
        "یان پەیوەندی بکە بە ژمارەی: +964 750 123 4567\n\n"
        "تیمەکەمان لە ماوەی 24 کاتژمێردا وەڵامت دەداتەوە."
    )
    
    bot.send_message(
        message.chat.id,
        registration_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

# دەستپێکردنی بۆت
if name == "__main__":
    print("بۆت دەستی پێکرد...")
    bot.infinity_polling()
