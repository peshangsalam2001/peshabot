import telebot
from telebot import types
import requests
import os
import subprocess
import traceback

API_TOKEN = '7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI'
bot = telebot.TeleBot(API_TOKEN)

# Reset webhook on startup
requests.get(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook")

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots"),
        types.InlineKeyboardButton("چۆنیەتی بەکارهێنانی بۆتەکە", callback_data='how_to_use'),
        types.InlineKeyboardButton("خاوەن بۆت", url="https://t.me/MasterLordBoss")
    )
    bot.send_message(
        message.chat.id,
        "بەخێربێی بۆ بۆتەکە!\n\nتکایە بەستەرێکی ڤیدیۆی یوتوب یان تیکتۆک بنێرە بۆ داگرتن.",
        reply_markup=markup
    )

# Tutorial video
@bot.callback_query_handler(func=lambda call: call.data == 'how_to_use')
def how_to_use(call):
    video_url = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4?Expires=1841246907&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=z6BkaPkTwhTwjl-QZw6VNroAuS7zbxxIboZclk8Ww1GTQpxK~M-03JNLXt5Ml6pReIyvxJGGKBGX60~uGI2S5Tev3QtMHz3hIa7iPTQIrfv1p32oTvwyycnFfvecpFAofB-4qGSvZ5YsynhnrpUJT-fH25ROpkGnj9xMo87KWlrd6E1G9sWP5PNwpnLkRMkoh2uZLyWA935JPLX0bJMRGdovqmrORlp7XvxoOom2vHg2zydq1JSDVDlbxGFsM3guN8GWSPSM-pfOymZfJY-r~ajDT8sD~fjDCUwji~zW~LCqLTYdwHhglJXmtOStjsmeXqn4JOU2Q85LtIM~LHRTgA__"
    bot.send_video(call.message.chat.id, video=video_url, caption="ئەم ڤیدیۆیە چۆنیەتی بەکارهێنەنی بۆتەکە ڕووندەکاتەوە")

# Handle video links
@bot.message_handler(func=lambda message: True)
def handle_links(message):
    url = message.text.strip()
    if not ("youtube.com" in url or "youtu.be" in url or "tiktok.com" in url):
        bot.reply_to(message, "تکایە بەستەرێکی ڤیدیۆ بنێرە (YouTube/TikTok).")
        return

    msg = bot.reply_to(message, "داگرتن لە ڕێگەی یوتیوب دەست پێکرد ... تکایە چاوەڕێ بکە")

    try:
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            "yt-dlp",
            "-f", "mp4",
            "--output", f"{output_dir}/%(title).40s.%(ext)s",
            url
        ]
        subprocess.run(cmd, check=True)

        files = os.listdir(output_dir)
        files.sort(key=lambda x: os.path.getctime(os.path.join(output_dir, x)), reverse=True)

        video_path = os.path.join(output_dir, files[0])
        file_size = os.path.getsize(video_path)

        if file_size > 50 * 1024 * 1024:
            bot.edit_message_text("قەبارەی ڤیدیۆکە زۆر گەورەیە، تکایە لینکێکی تر بنێرە.", message.chat.id, msg.message_id)
            os.remove(video_path)
            return

        with open(video_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="ڤیدیۆکەت بەسەرکەوتوویی داونلۆدکرا ✅")

        bot.delete_message(message.chat.id, msg.message_id)
        os.remove(video_path)

    except Exception as e:
        error_details = traceback.format_exc()
        bot.edit_message_text(
            f"هەڵەیەک ڕوویدا لە کاتی داگرتنەوە، تکایە دووبارە هەوڵ بدە.\n\n**هەڵەکە:**\n`{str(e)}`",
            message.chat.id,
            msg.message_id,
            parse_mode="Markdown"
        )

# Start bot polling
print("Bot is running...")
bot.infinity_polling()