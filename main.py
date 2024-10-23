import telebot
import yt_dlp
import os

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

# Path to store downloaded videos
VIDEO_PATH = 'videos/'
if not os.path.exists(VIDEO_PATH):
    os.makedirs(VIDEO_PATH)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a Facebook Reel link, and I will download the video for you.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Just send me a Facebook Reel link, and I will download the video for you.")

@bot.message_handler(func=lambda message: True)
def download_facebook_reel(message):
    url = message.text.strip()
    if "facebook.com" not in url:
        bot.reply_to(message, "Please send a valid Facebook Reel link.")
        return
    
    bot.reply_to(message, "Downloading your video. Please wait...")
    
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': VIDEO_PATH + '%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = ydl.prepare_filename(info_dict)

        with open(video_title, 'rb') as video:
            bot.send_video(message.chat.id, video)
        
        # Clean up the video file after sending
        os.remove(video_title)
        
    except Exception as e:
        bot.reply_to(message, "Sorry, I couldn't download the video.")
        print(e)

bot.polling()