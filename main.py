import telebot
import requests

bot_token = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Send the Instagram reel URL to download.")

@bot.message_handler(func=lambda m: True)
def download_reel(message):
    reel_url = message.text
    api_url = "https://indown.io/reels"
    
    try:
        # Send POST request to InDown.io
        response = requests.post(api_url, data={"url": reel_url})
        html_content = response.text

        # Find .mp4 link in HTML response (assuming it's available directly)
        mp4_links = [line for line in html_content.split('"') if line.endswith(".mp4")]
        
        if mp4_links:
            download_link = mp4_links[0]
            bot.send_message(message.chat.id, download_link)
        else:
            bot.send_message(message.chat.id, "Could not find a download link. Please check the URL.")

    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred: " + str(e))

bot.infinity_polling()