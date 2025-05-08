import re
import time
import requests
import telebot
from telebot import types

BOT_TOKEN = '7835872937:AAHmy808cQtDdMysSxlli_RlbVKOBkkyApA'
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL = "@KurdishBots"
ADMIN = "@MasterLordBoss"

user_last_download_time = {}
awaiting_tiktok_link = set()  # Track users who clicked download button or sent /download and waiting for link

def is_member(user_id):
    try:
        return bot.get_chat_member(CHANNEL, user_id).status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots"))
    markup.row(types.InlineKeyboardButton("دابەزاندنی ڤیدیۆی تیکتۆک", callback_data='tiktok_download'))
    markup.row(types.InlineKeyboardButton("چۆنیاتی بەکارهێنانی بۆتەکە", callback_data='howto'))
    markup.row(types.InlineKeyboardButton("پەیوەندیم پێوەبکە", url=f"https://t.me/{ADMIN[1:]}"))
    return markup

def is_valid_tiktok_link(text):
    # Simple regex for tiktok links
    pattern = r'https?://(www\.|vm\.)?tiktok\.com/.+'
    return re.match(pattern, text)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_member(user_id):
        name = message.from_user.first_name or ""
        text = f"سڵاو بەڕێز ناوی یەکەمی بەکارهێنەر {name}، ئەم بۆتە تایبەتە بە داونلۆدکردنی ڤیدیۆی تیکتۆک بە بەرزترین کوالیتی."
        bot.send_message(message.chat.id, text, reply_markup=main_markup())
    else:
        bot.send_message(message.chat.id, f"ببورە، پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'tiktok_download':
        bot.send_message(call.message.chat.id, "تکایە لینکی ڤیدیۆکە بنێرە تاکو داونلۆدی بکەم بۆت")
        awaiting_tiktok_link.add(call.from_user.id)
    elif call.data == 'howto':
        bot.send_message(call.message.chat.id,
                         "1. لینکێکی تیکتۆک بنێرە\n2. چاوەڕوانبە تاکو ڤیدیۆکەت بۆ دەنێرم\n\nبۆ پەیوەندی: @MasterLordBoss")

@bot.message_handler(commands=['download'])
def download_command(message):
    user_id = message.from_user.id
    if not is_member(user_id):
        bot.reply_to(message, f"ببورە، پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")
        return
    bot.send_message(message.chat.id, "تکایە لینکی ڤیدیۆکە بنێرە تاکو داونلۆدی بکەم بۆت")
    awaiting_tiktok_link.add(user_id)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    if user_id in awaiting_tiktok_link:
        awaiting_tiktok_link.discard(user_id)
        if not is_valid_tiktok_link(text):
            bot.reply_to(message, "ببورە لینکەکە دروست نیە، تکایە دڵنیابەرەوە لە لینکەکەت پاشان بینێرە ❌")
            return
        # Check cooldown
        now = time.time()
        last_time = user_last_download_time.get(user_id, 0)
        if now - last_time < 15:
            bot.reply_to(message, "تکایە ١٥ چرکە چاوەڕوانبە پاشان لینکێکی نوێ بنێرە 🚫")
            return
        user_last_download_time[user_id] = now
        download_and_send_tiktok(message, text)
    else:
        # If user sends /start handled above, so here only other commands or texts
        if text.startswith('/') and text.lower() != '/start':
            bot.reply_to(message, "تکایە کۆماندی /download بنێرە بۆ ئەوەی ڤیدیۆی تیکتۆک داونلۆدبکەی")
        else:
            send_welcome(message)

def get_tiktok_api_links(tiktok_url):
    api_url = f"https://tikwm.com/api/?url={tiktok_url}"
    try:
        res = requests.get(api_url, timeout=30).json()
        if not res.get("data"):
            return []
        qualities = []
        # TikWM keys from best to lower quality
        for key in ['play', 'play_1080p', 'play_720p', 'play_480p', 'play_360p']:
            link = res["data"].get(key)
            if link:
                qualities.append(link)
        return qualities
    except Exception:
        return []

def download_and_send_tiktok(message, tiktok_url):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ چاوەڕوانبە، ڤیدیۆکەت دابەزێنرێت...")
    qualities = get_tiktok_api_links(tiktok_url)
    if not qualities:
        bot.edit_message_text("❌ نەتوانرا ڤیدیۆکە بدۆزرێتەوە. تکایە لینکەکە دووبارە سەیر بکە.", chat_id, msg.message_id)
        return

    for video_url in qualities:
        try:
            video_response = requests.get(video_url, timeout=60)
            if video_response.status_code == 200:
                file_size = len(video_response.content)
                if file_size <= 50 * 1024 * 1024:
                    caption = ("بەسەرکەوتوویی ڤیدیۆکە بە بەرزترین کوالیتی داونلۆدکرا ✅\n"
                               "بۆ ئەوەی چەندین بۆتی هاوشێوەت دەستکەوێ تکایە سەردانی @KurdishBots بکە")
                    bot.send_video(chat_id, video_response.content, caption=caption)
                    bot.delete_message(chat_id, msg.message_id)
                    return
        except Exception:
            continue
    bot.edit_message_text("❌ قەبارەی هەموو کوالیتییەکان زیاترە لە ٥٠MB یان هەڵەیەک ڕوویدا.", chat_id, msg.message_id)

if __name__ == '__main__':
    bot.infinity_polling()
