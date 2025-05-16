import telebot
import yt_dlp as youtube_dl
import os

BOT_TOKEN = '7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI'
CHANNEL_LINK = 'https://t.me/YourChannel'
CONTACT_USERNAME = 'YourTelegramUsername'
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN)

# /start Command
@bot.message_handler(commands=['start'])
def start_handler(message):
    welcome_text = (
        "👋 بەخێربێیت بۆ بۆتی دابەزاندنی ڤیدیۆ!\n\n"
        "⬇️ ڤیدیۆ لە YouTube، Shorts، و TikTok دابەزێنە بە باشترین کوالیتی و بەرزترین خێرایی.\n"
        "تکایە یەکێک لە دوگمەکان هەلبژێرە:"
    )
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("📣 کانالی سەرەکی", url=CHANNEL_LINK),
        telebot.types.InlineKeyboardButton("⬇️ دابەزاندنی ڤیدیۆ", callback_data='get_video'),
    )
    markup.add(
        telebot.types.InlineKeyboardButton("❓ رێنمای بەکارهێنان", callback_data='help'),
        telebot.types.InlineKeyboardButton("📬 پەیوەندی پێوە بکە", url=f"https://t.me/{CONTACT_USERNAME}")
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Inline button handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'get_video':
        bot.send_message(call.message.chat.id, "🔗 تکایە لینکێکی ڤیدیۆی YouTube یان TikTok بنێرە:")
    elif call.data == 'help':
        bot.send_message(call.message.chat.id, (
            "🔸 تکایە لینکێکی ڤیدیۆ بنێرە (YouTube, Shorts, TikTok).\n"
            "🔸 ڤیدیۆکە بە باشترین quality دابەزێنرێت.\n"
            "🔸 ئەگەر ڤیدیۆکە گەورەتر بێت لە 50MB، quality دەکەم بۆ ئەوەی نێردراو بێت.\n"
            "🔸 تەنیا ڕێگە بە ڤیدیۆی دروستدەدرێت، نا ڕێگە بە شتە تر."
        ))

# Handle valid links
@bot.message_handler(func=lambda msg: any(x in msg.text for x in ['youtube.com', 'youtu.be', 'tiktok.com']))
def download_handler(message):
    url = message.text.strip()
    bot.send_message(message.chat.id, "⏳ دابەزاندن دەست پێکرد... تکایە چاوەڕێ بکە.")

    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0'
            }
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        size = os.path.getsize(file_path)
        if size > 50 * 1024 * 1024:
            # Retry with lower quality
            ydl_opts['format'] = 'worst'
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

        with open(file_path, 'rb') as f:
            if os.path.getsize(file_path) <= 50 * 1024 * 1024:
                bot.send_video(message.chat.id, f, caption="✅ ڤیدیۆکە دابەزرا!")
            else:
                bot.send_document(message.chat.id, f, caption="📦 ڤیدیۆیەکە گەورەیە، وەک document نێردرا.")

        os.remove(file_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ هەڵەیەک ڕوویدا:\n{str(e)}")

# Handle invalid messages
@bot.message_handler(func=lambda msg: True)
def invalid_handler(message):
    bot.send_message(message.chat.id, "❌ تکایە تەنها لینکێکی ڤیدیۆی YouTube یان TikTok بنێرە.")

# Start polling
bot.polling()