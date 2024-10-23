import telebot, pytesseract
from PIL import Image

bot = telebot.TeleBot('7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY')

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('image.jpg', 'wb') as new_file:
        new_file.write(downloaded_file)
    img = Image.open('image.jpg')
    text = pytesseract.image_to_string(img)
    bot.reply_to(message, text)

bot.infinity_polling()