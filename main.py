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
    patterns = [
        r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/watch\?v=',
        r'^(https?\:\/\/)?(www\.)?youtube\.com\/shorts\/',
        r'^(https?\:\/\/)?(www\.)?youtu\.be\/'
    ]
    return any(re.match(pattern, url) for pattern in patterns)

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

def download_youtube_video(message, url):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ تکایە چاوەڕوانبە، ڤیدیۆکەت دابەزێنرێت...")
    
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,
        'verbose': True,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'cookiefile': 'cookies.txt',
        'extractor_args': {
            'youtube': {
                'skip': [
                    'dash',
                    'hls'
                ]
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Failed to extract video info")
            
            file_path = ydl.prepare_filename(info)
            if os.path.getsize(file_path) > 50 * 1024 * 1024:
                os.remove(file_path)
                raise Exception("File size exceeds 50MB limit")
            
            with open(file_path, 'rb') as f:
                caption = ("ڤیدیۆکەت بەسەرکەوتوویی و بە بەرزتترین کوالیتی داونلۆدکرا ✅\n"
                           "بۆ سوودمەندبوون لە چەندین بۆتی هاوشێوە بەخۆڕایی تکایە سەردانی کەناڵەکەمان بکە @KurdishBots")
                bot.send_video(chat_id, f, caption=caption)
            
            os.remove(file_path)
            bot.delete_message(chat_id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ هەڵە لە دابەزاندنی ڤیدیۆ: {str(e)}", chat_id, msg.message_id)

# Rest of the code remains the same as previous version for TikTok handling and other functions...
# [Keep the TikTok download function and other existing code unchanged]