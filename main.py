import os
import telebot
import subprocess

# Replace with your own API token
API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a YouTube link and I'll download the video for you.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    video_url = message.text
    bot.reply_to(message, "Downloading video...")

    try:
        # Define the output directory and file name
        output_dir = 'downloads'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
        
        # Using you-get to download the video
        command = ['you-get', '-o', output_dir, video_url]
        subprocess.run(command, check=True)

        # Find the downloaded file (assuming it's the only file in the output directory)
        downloaded_files = os.listdir(output_dir)
        if downloaded_files:
            video_file_path = os.path.join(output_dir, downloaded_files[0])
            with open(video_file_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)

            # Clean up by removing the downloaded file
            os.remove(video_file_path)
        else:
            bot.reply_to(message, "Failed to find the downloaded video file.")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

bot.infinity_polling()