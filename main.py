import os
import telebot
import subprocess
import validators
from telebot import types

bot = telebot.TeleBot("7595180485:AAE5KKHtm3YHH1lo7cZqt4IDSIMsq8OyasI")

# Replace this with your actual channel username (without @)
MAIN_CHANNEL = "YourMainChannel"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        types.InlineKeyboardButton("Join Our Channel", url=f"https://t.me/{MAIN_CHANNEL}"),
        types.InlineKeyboardButton("Send Link to Download", switch_inline_query_current_chat=""),
        types.InlineKeyboardButton("How to Use the Bot", callback_data="how_to_use"),
        types.InlineKeyboardButton("Contact Creator", url="https://t.me/YourUsername")
    )
    bot.send_message(message.chat.id,
                     "Welcome! I can help you download videos from YouTube, Shorts, and TikTok.\nJust send me the link.",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "how_to_use":
        bot.send_message(call.message.chat.id,
                         "To use this bot:\n1. Copy a YouTube, Shorts, or TikTok link\n2. Paste it here\n3. I’ll download the video and send it to you!")

def is_valid_video_link(text):
    return (
        validators.url(text) and
        ("youtube.com" in text or "youtu.be" in text or "tiktok.com" in text)
    )

@bot.message_handler(func=lambda message: True)
def handle_links(message):
    text = message.text.strip()

    if is_valid_video_link(text):
        bot.send_chat_action(message.chat.id, 'upload_video')

        video_url = text
        video_file_path = "video.mp4"

        yt_dlp_command = [
            "yt-dlp",
            "-o", video_file_path,
            "-f", "mp4",
            "--no-playlist",
            video_url
        ]

        try:
            result = subprocess.run(
                yt_dlp_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            yt_output = result.stdout.decode('utf-8') + '\n' + result.stderr.decode('utf-8')

            if os.path.exists(video_file_path):
                # Check video size
                if os.path.getsize(video_file_path) > 50 * 1024 * 1024:
                    # Recompress to lower quality
                    compressed_path = "compressed_video.mp4"
                    ffmpeg_command = [
                        "ffmpeg", "-i", video_file_path,
                        "-vf", "scale=640:-2", "-preset", "fast",
                        "-crf", "28", compressed_path
                    ]
                    subprocess.run(ffmpeg_command)
                    os.remove(video_file_path)
                    video_file_path = compressed_path

                bot.send_video(message.chat.id, open(video_file_path, 'rb'), caption="Here is your video!")
                os.remove(video_file_path)
            else:
                bot.send_message(message.chat.id, "Download failed. See the details below:")

            # Always show yt-dlp output (success or fail)
            for i in range(0, len(yt_output), 4000):
                bot.send_message(message.chat.id, yt_output[i:i+4000])

        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred:\n{str(e)}")

    else:
        bot.send_message(message.chat.id, "❌ Please send a valid YouTube or TikTok video link.")

bot.infinity_polling()