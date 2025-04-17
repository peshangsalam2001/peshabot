import telebot
from pytube import YouTube

bot = telebot.TeleBot("7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🎬 Send me a YouTube link to download!")

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def download(msg):
    try:
        yt = YouTube(msg.text)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first()
        bot.send_message(msg.chat.id, f"⬇️ Downloading: {yt.title}")
        video = stream.download(filename='video.mp4')
        with open("video.mp4", "rb") as v:
            bot.send_video(msg.chat.id, v)
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Error: {e}")

bot.polling()
