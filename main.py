import os
import re
import time
import json
import requests
import telebot
from telebot import types
import yt_dlp

BOT_TOKEN = '7595180485:AAELAJ6ZWq2x-S5ruuQzbmSG89zrDqZtvLU'
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL = "@KurdishBots"
ADMIN = "@MasterLordBoss"
USER_DATA_FILE = 'bot_users.json'

TUTORIAL_VIDEO_URL = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4?..."

user_last_download_time = {}
user_waiting_for_link = set()
stats = {'users_started': set(), 'valid_links': 0}

def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f).get('users_started', []))
        except Exception:
            return set()
    return set()

def save_users(users):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users_started': list(users)}, f)

stats['users_started'] = load_users()

def is_member(user_id):
    try:
        return bot.get_chat_member(CHANNEL, user_id).status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots"))
    markup.row(types.InlineKeyboardButton("دابەزاندنی ڤیدیۆ", callback_data='download_video'))
    markup.row(types.InlineKeyboardButton("چۆنیەتی بەکارهێنانی بۆتەکە", callback_data='howto'))
    markup.row(types.InlineKeyboardButton("پەیوەندیم پێوەبکە", url=f"https://t.me/{ADMIN[1:]}"))
    return markup

def is_valid_tiktok_link(text):
    return re.search(r'(https?://)?(www\.)?(vm|vt)?\.?tiktok\.com/.+', text)

def is_valid_youtube_link(text):
    return re.search(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+', text)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in stats['users_started']:
        stats['users_started'].add(user_id)
        save_users(stats['users_started'])
    if is_member(user_id):
        name = message.from_user.first_name or ""
        bot.send_message(message.chat.id,
                         f"سڵاو {name}، ئەم بۆتە ڤیدیۆیەکانی تیکتۆک و یوتوب بە بەرزترین کوالیتی دابەزێنێت ✅",
                         reply_markup=main_markup())
    else:
        bot.send_message(message.chat.id, f"ببورە، تکایە یەکەم جۆینی کەناڵەکە بکە:\n{CHANNEL}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'howto':
        caption = "ئەم ڤیدیۆیە فێرکاری چۆنیەتی بەکارهێنانی بۆتەکەیە ✅"
        try:
            r = requests.get(TUTORIAL_VIDEO_URL, stream=True, timeout=60)
            if r.status_code == 200:
                bot.send_video(call.message.chat.id, r.content, caption=caption)
            else:
                bot.send_message(call.message.chat.id, "❌ نەتوانرا ڤیدیۆی ڕاهێنان باربکات.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ هەڵە لە ناردنی ڤیدیۆ: {str(e)}")
    elif call.data == 'download_video':
        user_id = call.from_user.id
        if is_member(user_id):
            user_waiting_for_link.add(user_id)
            bot.send_message(call.message.chat.id, "❗️ تکایە لینکی ڤیدیۆی یوتوب یاخود تیکتۆک بنێرە تاکو داونلۆدی بکەم")
        else:
            bot.send_message(call.message.chat.id, f"ببورە، یەکەم جۆینی کەناڵەکە بکە:\n{CHANNEL}")

def get_tiktok_api_links(url):
    api_url = f"https://tikwm.com/api/?url={url}"
    try:
        res = requests.get(api_url, timeout=30).json()
        if not res.get("data"):
            return []
        return [res["data"].get(k) for k in ['play_1080p', 'play', 'play_720p', 'play_480p', 'play_360p'] if res["data"].get(k)]
    except Exception:
        return []

def download_youtube_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': 'video.%(ext)s',
        'noplaylist': True,
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url']
    except Exception:
        return None

def send_downloaded_video(chat_id, video_url, caption):
    try:
        r = requests.get(video_url, timeout=60)
        if r.status_code == 200 and len(r.content) <= 50 * 1024 * 1024:
            bot.send_video(chat_id, r.content, caption=caption)
            return True
    except Exception:
        pass
    return False

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    if text == "/start":
        send_welcome(message)
        return

    if not is_member(user_id):
        bot.reply_to(message, f"ببورە، پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")
        return

    if user_id not in user_waiting_for_link:
        bot.reply_to(message, "☢️ تکایە لینکی ڤیدیۆی یوتوب یان تیکتۆک بنێرە، یان /start بنێرە بۆ گەڕانەوە")
        return

    now = time.time()
    if now - user_last_download_time.get(user_id, 0) < 15:
        bot.reply_to(message, "تکایە ١٥ چرکە چاوەڕوانبە پاشان لینکێکی نوێ بنێرە 🚫")
        return

    if is_valid_tiktok_link(text):
        user_last_download_time[user_id] = now
        stats['valid_links'] += 1
        user_waiting_for_link.discard(user_id)
        msg = bot.reply_to(message, "⏳ چاوەڕوانبە، ڤیدیۆی تیکتۆکە دابەزێنرێت...")
        links = get_tiktok_api_links(text)
        for link in links:
            if send_downloaded_video(message.chat.id, link,
                    "ڤیدیۆکەت بە بەرزترین کوالیتی داونلۆدکرا ✅\nتکایە سەردانی @KurdishBots بکە بۆ سوودمەند بوون لە چەندین بۆتی هاوشێوە 🤎"):
                bot.delete_message(message.chat.id, msg.message_id)
                return
        bot.edit_message_text("قەبارەی ڤیدیۆکە گەورەیە یان لینکەکەت هەڵەیە ❌", message.chat.id, msg.message_id)
    elif is_valid_youtube_link(text):
        user_last_download_time[user_id] = now
        stats['valid_links'] += 1
        user_waiting_for_link.discard(user_id)
        msg = bot.reply_to(message, "⏳ چاوەڕوانبە، ڤیدیۆی یوتوبە دابەزێنرێت...")
        video_url = download_youtube_video(text)
        if video_url and send_downloaded_video(message.chat.id, video_url,
                "ڤیدیۆکەت بە بەرزترین کوالیتی داونلۆدکرا ✅\nتکایە سەردانی @KurdishBots بکە بۆ سوودمەند بوون لە چەندین بۆتی هاوشێوە 🤎"):
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("ببورە لینکەکەت دروست نیە یان قەبارەی ڤیدیۆکە زۆر گەورەیە ❌", message.chat.id, msg.message_id)
    else:
        bot.reply_to(message, "❌ تکایە لینکێکی دروست بنێرە (یوتوب یان تیکتۆک)")

if __name__ == '__main__':
    bot.infinity_polling()