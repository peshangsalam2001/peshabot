import os
import re
import time
import json
import requests
import telebot
from telebot import types
import yt_dlp

TOKEN = "7595180485:AAELAJ6ZWq2x-S5ruuQzbmSG89zrDqZtvLU"
CHANNEL = "@KurdishBots"
ADMIN = "@MasterLordBoss"
OWNER_USERNAME = "MasterLordBoss"
USER_DATA_FILE = 'bot_users.json'

bot = telebot.TeleBot(TOKEN)

# Persistent user storage functions
def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('users_started', []))
        except Exception:
            return set()
    return set()

def save_users(users):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users_started': list(users)}, f)

# Initialize stats
stats = {
    'users_started': load_users(),
    'valid_links': 0,
}

user_last_download_time = {}

TUTORIAL_VIDEO_URL = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4?Expires=1841246907&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=z6BkaPkTwhTwjl-QZw6VNroAuS7zbxxIboZclk8Ww1GTQpxK~M-03JNLXt5Ml6pReIyvxJGGKBGX60~uGI2S5Tev3QtMHz3hIa7iPTQIrfv1p32oTvwyycnFfvecpFAofB-4qGSvZ5YsynhnrpUJT-fH25ROpkGnj9xMo87KWlrd6E1G9sWP5PNwpnLkRMkoh2uZLyWA935JPLX0bJMRGdovqmrORlp7XvxoOom2vHg2zydq1JSDVDlbxGFsM3guN8GWSPSM-pfOymZfJY-r~ajDT8sD~fjDCUwji~zW~LCqLTYdwHhglJXmtOStjsmeXqn4JOU2Q85LtIM~LHRTgA__"

def is_member(user_id):
    try:
        return bot.get_chat_member(CHANNEL, user_id).status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def is_youtube_url(url):
    return re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+', url)

def is_tiktok_url(url):
    return re.match(r'https?://(www\.tiktok\.com|vt\.tiktok\.com|vm\.tiktok\.com)/.+', url)

def is_valid_link(text):
    return is_youtube_url(text) or is_tiktok_url(text)

def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots"))
    markup.row(types.InlineKeyboardButton("دابەزاندنی ڤیدیۆ", callback_data='download_video'))
    markup.row(types.InlineKeyboardButton("چۆنیەتی بەکارهێنانی بۆتەکە", callback_data='howto'))
    markup.row(types.InlineKeyboardButton("پەیوەندیم پێوەبکە", url=f"https://t.me/{ADMIN[1:]}"))
    return markup

def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in stats['users_started']:
        stats['users_started'].add(user_id)
        save_users(stats['users_started'])
    if is_member(user_id):
        text = ("بەخێربێن بۆ بۆتی داونلۆدکردنی ڤیدیۆ لە سەرجەم سۆشیال میدیاکان 🤎\n\n"
                "سەردانی @KurdishBots بکە بۆ سوودمەندبوون لە چەندین بۆتی ناوەزە بە خۆڕایی 👑")
        bot.send_message(message.chat.id, text, reply_markup=main_markup())
    else:
        bot.send_message(message.chat.id,
                         f"بەخێربێن بۆ بۆتی داونلۆدکردنی ڤیدیۆ لەم پلاتفۆڕمانە (یوتوب، تیکتۆک) ✅\n\n"
                         f"تکایە جۆینی ئەم کەناڵە بکە بۆ ئاگاداربوون لە هەموو گۆڕانکاریەکانی بۆتەکە و بەدەستهێنانی چەندین بۆتی بەسوودی هاوشێوە 👑\n"
                         f"https://t.me/KurdishBots")

@bot.message_handler(commands=['start'])
def start_handler(message):
    send_welcome(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'download_video':
        bot.send_message(call.message.chat.id, "تکایە لینکی ڤیدیۆکەت بنێرە")
    elif call.data == 'howto':
        caption = "ئەم ڤیدیۆیە فێرکاری چۆنیەتی بەکارهێنانی بۆتەکەیە ✅"
        try:
            video_response = requests.get(TUTORIAL_VIDEO_URL, stream=True, timeout=60)
            if video_response.status_code == 200:
                bot.send_video(call.message.chat.id, video_response.content, caption=caption)
            else:
                bot.send_message(call.message.chat.id, "❌ نەتوانرا ڤیدیۆی ڕاهێنان باربکات.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ هەڵە لە ناردنی ڤیدیۆ: {str(e)}")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.username == OWNER_USERNAME:
        user_count = len(stats['users_started'])
        valid_links = stats['valid_links']
        text = (
            f"📊 نوێترین زانیاری بۆت:\n"
            f"👥 ژمارەی بەکارهێنەران: {user_count}\n"
            f"🎬 ژمارەی لینکی ڤیدیۆی دروست داواکراوە: {valid_links}\n"
            f"⏰ کاتی داواکاری: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        )
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "فەرمانەکە تەنها بۆ خاوەنی بۆتە.")

@bot.message_handler(commands=['post'])
def post_command(message):
    if message.from_user.username == OWNER_USERNAME:
        msg = bot.send_message(message.chat.id, "تکایە پەیامەکەت بنێرە تاکو منیش بینێرم بۆ بەکارهێنەران")
        bot.register_next_step_handler(msg, process_post)
    else:
        bot.delete_message(message.chat.id, message.message_id)

def process_post(message):
    if message.from_user.username == OWNER_USERNAME:
        sent = 0
        errors = 0
        total = len(stats['users_started'])
        for user_id in stats['users_started']:
            try:
                if message.content_type == 'text':
                    bot.send_message(user_id, message.text)
                elif message.content_type == 'photo':
                    bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video':
                    bot.send_video(user_id, message.video.file_id, caption=message.caption)
                sent += 1
                time.sleep(0.5)
            except Exception:
                errors += 1
        bot.send_message(message.chat.id, f"✅ نێردرا بۆ {sent} بەکارهێنەر | شکستی هێنا بۆ {errors}")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    if not is_member(user_id):
        bot.reply_to(message, f"ببورە، پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")
        return

    if text == '/start':
        send_welcome(message)
        return

    if is_valid_link(text):
        now = time.time()
        last_time = user_last_download_time.get(user_id, 0)
        if now - last_time < 15:
            bot.reply_to(message, "تکایە ١٥ چرکە چاوەڕوانبە پاشان لینکێکی نوێ بنێرە 🚫")
            return
        user_last_download_time[user_id] = now
        stats['valid_links'] += 1
        
        if is_youtube_url(text):
            download_youtube_video(message, text)
        elif is_tiktok_url(text):
            download_tiktok_video(message, text)
    else:
        bot.reply_to(message, "ببورە لینکەکەت هەڵەیە❌")

def download_youtube_video(message, url):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ تکایە چاوەڕوانبە، ڤیدیۆکەت دابەزێنرێت...")
    formats = [
        'bestvideo[height<=1080]+bestaudio/best',
        'bestvideo[height<=720]+bestaudio/best',
        'bestvideo[height<=480]+bestaudio/best',
        'bestvideo[height<=360]+bestaudio/best',
    ]
    for fmt in formats:
        try:
            ydl_opts = {
                'format': fmt,
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if os.path.getsize(file_path) > 50 * 1024 * 1024:
                    os.remove(file_path)
                    continue
                with open(file_path, 'rb') as f:
                    caption = ("ڤیدیۆکەت بەسەرکەوتوویی و بە بەرزتترین کوالیتی داونلۆدکرا ✅\n"
                               "بۆ سوودمەندبوون لە چەندین بۆتی هاوشێوە بەخۆڕایی تکایە سەردانی کەناڵەکەمان بکە @KurdishBots")
                    bot.send_video(chat_id, f, caption=caption)
                os.remove(file_path)
                bot.delete_message(chat_id, msg.message_id)
                return
        except Exception:
            continue
    bot.edit_message_text("❌ نەتوانرا ڤیدیۆکە دابەزێنرێت لەبەر قەبارەی گەورە یان هەڵەیەک ڕوویدا", chat_id, msg.message_id)

def get_tiktok_api_links(tiktok_url):
    api_url = f"https://tikwm.com/api/?url={tiktok_url}"
    try:
        res = requests.get(api_url, timeout=30).json()
        if not res.get("data"):
            return []
        qualities = []
        for key in ['play', 'play_1080p', 'play_720p', 'play_480p', 'play_360p']:
            link = res["data"].get(key)
            if link:
                qualities.append(link)
        return qualities
    except Exception:
        return []

def download_tiktok_video(message, tiktok_url):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ تکایە چاوەڕوانبە، ڤیدیۆکەت دابەزێنرێت...")
    qualities = get_tiktok_api_links(tiktok_url)
    if not qualities:
        bot.edit_message_text("لینکەکەت هەڵەیە، تکایە دڵنیابەرەوە لە لینکەکەت پاشان بینێرە ❌", chat_id, msg.message_id)
        return
    for video_url in qualities:
        try:
            video_response = requests.get(video_url, timeout=60)
            if video_response.status_code == 200:
                file_size = len(video_response.content)
                if file_size <= 50 * 1024 * 1024:
                    caption = ("ڤیدیۆکەت بەسەرکەوتوویی و بە بەرزتترین کوالیتی داونلۆدکرا ✅\n"
                               "بۆ سوودمەندبوون لە چەندین بۆتی هاوشێوە بەخۆڕایی تکایە سەردانی کەناڵەکەمان بکە @KurdishBots")
                    bot.send_video(chat_id, video_response.content, caption=caption)
                    bot.delete_message(chat_id, msg.message_id)
                    return
        except Exception:
            continue
    bot.edit_message_text("قەبارەی ئەم ڤیدیۆیە لە 50MB زیاترە بۆیە داونلۆد ناکرێ:", chat_id, msg.message_id)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()