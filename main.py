import os
import re
import time
import json
import requests
import telebot
from telebot import types
import yt_dlp

TOKEN = "7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI"
CHANNEL = "@KurdishBots"
ADMIN = "@MasterLordBoss"
OWNER_USERNAME = "MasterLordBoss"
USER_DATA_FILE = 'bot_users.json'
EXPORT_FILE = 'exported_users.txt'

bot = telebot.TeleBot(TOKEN)

# Persistent user storage
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

stats = {
    'users_started': load_users(),
    'valid_links': 0,
}

user_last_download_time = {}
broadcast_mode = {}

TUTORIAL_VIDEO_URL = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4?..."

def is_member(user_id):
    try:
        return bot.get_chat_member(CHANNEL, user_id).status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def is_youtube_url(url):
    patterns = [r'(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)']
    return any(re.search(pattern, url) for pattern in patterns)

def is_tiktok_url(url):
    return re.search(r'tiktok\.com/', url)

def is_facebook_url(url):
    patterns = [r'facebook\.com/.+/videos/.+', r'facebook\.com/reel/', r'facebook\.com/story\.php\?story_fbid=']
    return any(re.search(pattern, url) for pattern in patterns)

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
        bot.send_message(message.chat.id, "بەخێربێن...", reply_markup=main_markup())
    else:
        bot.send_message(message.chat.id, f"سەرەتا پێویستە جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'download':
        bot.send_message(call.message.chat.id, "🎬 تکایە لینکی ڤیدیۆکەت بنێرە (یوتوب / تیکتۆک / فەیسبووک)")
    elif call.data == 'howto':
        bot.send_video(call.message.chat.id, TUTORIAL_VIDEO_URL, caption="🎬 فێرکاری بەکارهێنانی بۆت")

# Admin-only commands
@bot.message_handler(commands=['stats', 'broadcast', 'reset', 'export_users'])
def admin_commands(message):
    if message.from_user.username != OWNER_USERNAME:
        return

    cmd = message.text.strip().lower()

    if cmd == '/stats':
        bot.send_message(message.chat.id,
                         f"👥 ژمارەی بەکارهێنەران: {len(stats['users_started'])}\n"
                         f"📥 داونلۆدی ڤیدیۆیە بەسەرکەوتو: {stats['valid_links']}")

    elif cmd == '/broadcast':
        broadcast_mode[message.chat.id] = True
        bot.send_message(message.chat.id, "✉️ نوسینی نامەی بڵاوکراو: تکایە نامەکە بنێرە.")

    elif cmd == '/reset':
        stats['valid_links'] = 0
        bot.send_message(message.chat.id, "✅ ئەنجامی داونلۆد سڕایەوە.")

    elif cmd == '/export_users':
        with open(EXPORT_FILE, 'w') as f:
            for uid in stats['users_started']:
                f.write(f"{uid}\n")
        with open(EXPORT_FILE, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="📁 لیستی بەکارهێنەران")

# Handle broadcast message
@bot.message_handler(func=lambda msg: broadcast_mode.get(msg.chat.id, False))
def handle_broadcast(msg):
    if msg.from_user.username != OWNER_USERNAME:
        return

    sent = 0
    failed = 0
    for user_id in stats['users_started']:
        try:
            bot.send_message(user_id, msg.text)
            sent += 1
        except Exception:
            failed += 1

    broadcast_mode[msg.chat.id] = False
    bot.send_message(msg.chat.id, f"📤 ناردرا بۆ {sent} کەس ✅\n❌ سەرکەوتوو نەبوو: {failed}")

# Handle all other messages (links)
@bot.message_handler(func=lambda msg: True)
def handle_link(msg):
    text = msg.text.strip()
    user_id = msg.from_user.id

    if text.startswith("/"):
        return

    if not is_member(user_id):
        bot.send_message(user_id, f"پێویستە جۆینی کەناڵ بکەیت:\n{CHANNEL}")
        return

    if is_youtube_url(text) or is_tiktok_url(text) or is_facebook_url(text):
        stats['valid_links'] += 1
        bot.reply_to(msg, "⏬ لینک وەرگیرا... (هەڵبژاردنی باشترین کوالیتی)")
        # Place download logic here (your existing download_media logic)
    else:
        bot.send_message(msg.chat.id, "❌ تکایە تەنها لینکی ڤیدیۆ بنێرە (یوتوب / تیکتۆک / فەیسبووک)")

bot.polling()