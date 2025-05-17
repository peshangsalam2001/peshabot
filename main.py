import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import validators
import yt_dlp
import os
import uuid

BOT_TOKEN = '7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI'
bot = telebot.TeleBot(BOT_TOKEN)

# Helper function to check video size
def get_file_size(path):
    return os.path.getsize(path) / (1024 * 1024)  # in MB

# Start command handler
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots"),
        InlineKeyboardButton("خاوەن بۆت", url="https://t.me/MasterLordBoss")
    )
    markup.add(
        InlineKeyboardButton("چۆنیەتی بەکارهێنانی بۆتەکە", callback_data="how_to_use")
    )
    bot.send_message(
        message.chat.id,
        "بۆ داونلۆدی ڤیدیۆ، لینکی یوتیوب یان تیکتۆک بنێرە.",
        reply_markup=markup
    )

# Callback handler for "How to use"
@bot.callback_query_handler(func=lambda call: call.data == "how_to_use")
def send_usage_video(call):
    video_url = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4?Expires=1841246907&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=z6BkaPkTwhTwjl-QZw6VNroAuS7zbxxIboZclk8Ww1GTQpxK~M-03JNLXt5Ml6pReIyvxJGGKBGX60~uGI2S5Tev3QtMHz3hIa7iPTQIrfv1p32oTvwyycnFfvecpFAofB-4qGSvZ5YsynhnrpUJT-fH25ROpkGnj9xMo87KWlrd6E1G9sWP5PNwpnLkRMkoh2uZLyWA935JPLX0bJMRGdovqmrORlp7XvxoOom2vHg2zydq1JSDVDlbxGFsM3guN8GWSPSM-pfOymZfJY-r~ajDT8sD~fjDCUwji~zW~LCqLTYdwHhglJXmtOStjsmeXqn4JOU2Q85LtIM~LHRTgA__"
    bot.send_video(call.message.chat.id, video=video_url, caption="ئەم ڤیدیۆیە چۆنیەتی بەکارهێنەنی بۆتەکە ڕووندەکاتەوە")

# Video download handler
@bot.message_handler(func=lambda message: True)
def handle_video_link(message):
    url = message.text.strip()
    if not validators.url(url):
        bot.reply_to(message, "تکایە بەستەرێکی دروست بنێرە!")
        return

    msg = bot.reply_to(message, "داونلۆدکردن دەست پێکرد... تکایە چاوەڕێ بکە")

    ydl_opts = {
        'outtmpl': f'{uuid.uuid4()}.%(ext)s',
        'format': 'best[ext=mp4]/best',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        size_mb = get_file_size(file_path)
        if size_mb > 50:
            bot.send_message(message.chat.id, "ببورە! ڤیدیۆکە گەورەترە لە 50MB، ناتوانرێت نێردرێت.")
            os.remove(file_path)
            return

        with open(file_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video=video_file, caption="ڤیدیۆکەت بەسەرکەوتوویی داونلۆدکرا ✅")

        os.remove(file_path)

    except Exception as e:
        bot.send_message(message.chat.id, "هەڵەیەک ڕووی دا! تکایە دواتر هەوڵ بدە.")
        print(f"Download error: {e}")

bot.polling()