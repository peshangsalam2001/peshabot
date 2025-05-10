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

# Tutorial video URL
TUTORIAL_VIDEO_URL = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4?Expires=1841246907&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=z6BkaPkTwhTwjl-QZw6VNroAuS7zbxxIboZclk8Ww1GTQpxK~M-03JNLXt5Ml6pReIyvxJGGKBGX60~uGI2S5Tev3QtMHz3hIa7iPTQIrfv1p32oTvwyycnFfvecpFAofB-4qGSvZ5YsynhnrpUJT-fH25ROpkGnj9xMo87KWlrd6E1G9sWP5PNwpnLkRMkoh2uZLyWA935JPLX0bJMRGdovqmrORlp7XvxoOom2vHg2zydq1JSDVDlbxGFsM3guN8GWSPSM-pfOymZfJY-r~ajDT8sD~fjDCUwji~zW~LCqLTYdwHhglJXmtOStjsmeXqn4JOU2Q85LtIM~LHRTgA__"

def is_member(user_id):
    try:
        return bot.get_chat_member(CHANNEL, user_id).status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def is_youtube_url(url):
    patterns = [
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)',
        r'(https?://)?(m\.youtube\.com/watch\?v=)',
        r'(https?://)?(music\.youtube\.com/watch\?v=)'
    ]
    return any(re.search(pattern, url) for pattern in patterns)

def is_tiktok_url(url):
    return re.search(r'https?://(www\.tiktok\.com|vt\.tiktok\.com|vm\.tiktok\.com)/', url)

def is_valid_link(text):
    return is_youtube_url(text) or is_tiktok_url(text)

def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots"))
    markup.row(types.InlineKeyboardButton("دابەزاندنی ڤیدیۆ", callback_data='download'))
    markup.row(types.InlineKeyboardButton("چۆنیەتی بەکارهێنان", callback_data='howto'))
    markup.row(types.InlineKeyboardButton("پەیوەندی", url=f"https://t.me/{ADMIN[1:]}"))
    return markup

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    if user_id not in stats['users_started']:
        stats['users_started'].add(user_id)
        save_users(stats['users_started'])
    
    if is_member(user_id):
        bot.send_message(message.chat.id, 
                        "بەخێربێن بۆ بۆتی داونلۆدکردنی ڤیدیۆ لە سەرجەم سۆشیال میدیاکان 🤎\n\n"
                        "سەردانی @KurdishBots بکە بۆ چەندین بۆتی تری بەسوود 👑", 
                        reply_markup=main_markup())
    else:
        bot.send_message(message.chat.id,
                        "بۆ بەکارهێنانی بۆتەکە سەرەتا پێویستە جۆینی کەناڵەکەمان بکەیت:\n"
                        f"{CHANNEL}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'download':
        bot.send_message(call.message.chat.id, "📥 تکایە لینکی ڤیدیۆکەت بنێرە (یوتوب/تیکتۆک)")
    elif call.data == 'howto':
        try:
            bot.send_video(call.message.chat.id, TUTORIAL_VIDEO_URL, 
                          caption="🎬 فێرکاری بەکارهێنانی بۆت")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ هەڵە لە بارکردنی ڤیدیۆ: {str(e)}")

def download_media(message, url):
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = bot.reply_to(message, "🔍 چاوەڕوانبە... پشکنینی لینک")
    
    try:
        if is_youtube_url(url):
            handle_youtube(url, chat_id, msg.message_id)
        elif is_tiktok_url(url):
            handle_tiktok(url, chat_id, msg.message_id)
        else:
            bot.edit_message_text("❌ جۆری لینک نەناسێنرا", chat_id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ هەڵە: {str(e)}", chat_id, msg.message_id)
    finally:
        user_last_download_time[user_id] = time.time()

def handle_youtube(url, chat_id, msg_id):
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'outtmpl': 'downloads/%(title).100s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt',  # Make sure this file exists and is valid
        'max_filesize': 50 * 1024 * 1024,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    bot.send_video(chat_id, f, caption="✅ ڤیدیۆکەت بە سەرکەوتوویی دابەزێنرا\n@KurdishBots")
                os.remove(file_path)
                bot.delete_message(chat_id, msg_id)
            else:
                bot.edit_message_text("❌ ڤیدیۆکە نەدۆزرایەوە دوای دابەزاندن", chat_id, msg_id)
    except yt_dlp.utils.DownloadError as e:
        if "File is larger than max-filesize" in str(e):
            bot.edit_message_text("❌ قەبارەی ڤیدیۆکە لە 50MB زیاترە", chat_id, msg_id)
        else:
            bot.edit_message_text(f"❌ هەڵە لە دابەزاندن:\n{str(e)}", chat_id, msg_id)
    except Exception as e:
        bot.edit_message_text(f"❌ هەڵەی نەناسراو:\n{str(e)}", chat_id, msg_id)

def handle_tiktok(url, chat_id, msg_id):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=30).json()
        
        if not response.get('data'):
            raise Exception("هیچ داتایەک نەدۆزرایەوە")
            
        video_url = response['data'].get('play') or response['data'].get('wmplay')
        if not video_url:
            raise Exception("نەتوانرا لینکی ڤیدیۆ بدۆزرێتەوە")
            
        video_data = requests.get(video_url, timeout=60).content
        if len(video_data) > 50 * 1024 * 1024:
            raise Exception("قەبارەی ڤیدیۆکە لە 50MB زیاترە")
            
        bot.send_video(chat_id, video_data, caption="✅ ڤیدیۆی تیکتۆک بە سەرکەوتوویی دابەزێنرا\n@KurdishBots")
        bot.delete_message(chat_id, msg_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ هەڵە لە دابەزاندنی تیکتۆک: {str(e)}", chat_id, msg_id)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""
    
    if not is_member(user_id):
        bot.reply_to(message, f"❌ تکایە سەرەتا جۆینی کەناڵەکەمان بکە:\n{CHANNEL}")
        return
    
    if text == '/start':
        start_handler(message)
        return
    
    if not is_valid_link(text):
        bot.reply_to(message, "❌ لینکێکی دروست بنێرە (یوتوب/تیکتۆک)")
        return
    
    last_time = user_last_download_time.get(user_id, 0)
    if time.time() - last_time < 15:
        bot.reply_to(message, "⏳ تکایە ١٥ چرکە چاوەڕوانبە پێش ناردنی لینکی نوێ")
        return
    
    stats['valid_links'] += 1
    download_media(message, text)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()