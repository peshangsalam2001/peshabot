import telebot
import easyocr
import requests
from io import BytesIO
from PIL import Image

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'

bot = telebot.TeleBot(API_TOKEN)
reader = easyocr.Reader(['en', 'ckb', 'ar'])  # English, Kurdish Sorani, Arabic

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me an image, and I'll extract the text for you (supports English, Kurdish Sorani, and Arabic).")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file = requests.get(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}')
    image = Image.open(BytesIO(file.content))

    # Extract text from the image
    results = reader.readtext(BytesIO(file.content))
    extracted_text = "\n".join([result[1] for result in results])

    bot.reply_to(message, extracted_text)

bot.polling()