import telebot
import yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace with your bot token and channel username
TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
CHANNEL_USERNAME = "@KurdishBots"

bot = telebot.TeleBot(TOKEN)

# Check if user is member of channel
def is_member(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if not is_member(message.from_user.id):
        bot.send_message(message.chat.id, "Please join the channel first: " + CHANNEL_USERNAME)
        return
    markup = InlineKeyboardMarkup()
    btn_video = InlineKeyboardButton("Download Video", callback_data="video")
    btn_shorts = InlineKeyboardButton("Download Shorts", callback_data="shorts")
    markup.add(btn_video, btn_shorts)
    bot.send_message(message.chat.id, "Welcome! Choose what to download:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data in ["video", "shorts"]:
        bot.send_message(call.message.chat.id, f"Please send the YouTube {call.data} link.")
        bot.register_next_step_handler(call.message, lambda m: download_video(m, call.data))

def download_video(message, media_type):
    if not is_member(message.from_user.id):
        bot.send_message(message.chat.id, "Please join the channel first: " + CHANNEL_USERNAME)
        return

    url = message.text
    if not url.startswith(('http://', 'https://')):
        bot.send_message(message.chat.id, "Invalid URL. Please send a valid YouTube link.")
        return

    try:
        ydl_opts = {'outtmpl': '%(title)s.%(ext)s'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            file_path = ydl.prepare_filename(info)
            ydl.download([url])
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

print("Bot is running...")
bot.infinity_polling()