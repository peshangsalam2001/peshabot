import telebot
from PIL import Image, ImageDraw, ImageFont

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

def ask_for_info(chat_id, info, question):
    user_data[chat_id] = user_data.get(chat_id, {})
    user_data[chat_id]['state'] = info
    bot.send_message(chat_id, question)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    ask_for_info(chat_id, 'full_name', "What is your full name?")

@bot.message_handler(func=lambda message: True)
def collect_info(message):
    chat_id = message.chat.id
    state = user_data.get(chat_id, {}).get('state')

    if state == 'full_name':
        user_data[chat_id]['full_name'] = message.text
        ask_for_info(chat_id, 'age', "What is your age?")
    elif state == 'age':
        user_data[chat_id]['age'] = message.text
        ask_for_info(chat_id, 'place', "Where are you from?")
    elif state == 'place':
        user_data[chat_id]['place'] = message.text
        ask_for_info(chat_id, 'graduate', "What is your highest education?")
    elif state == 'graduate':
        user_data[chat_id]['graduate'] = message.text
        ask_for_info(chat_id, 'languages', "What languages do you speak?")
    elif state == 'languages':
        user_data[chat_id]['languages'] = message.text
        ask_for_info(chat_id, 'skills', "What are your skills?")
    elif state == 'skills':
        user_data[chat_id]['skills'] = message.text
        ask_for_info(chat_id, 'experiences', "What are your experiences?")
    elif state == 'experiences':
        user_data[chat_id]['experiences'] = message.text
        ask_for_info(chat_id, 'picture', "Please send your picture.")
    elif state == 'picture' and message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f"{chat_id}_profile.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        
        user_data[chat_id]['picture'] = f"{chat_id}_profile.jpg"
        bot.send_message(chat_id, "Creating your CV...")
        create_cv(chat_id)
    else:
        bot.send_message(chat_id, "Please follow the instructions and send a valid response.")

def create_cv(chat_id):
    data = user_data[chat_id]
    cv_image = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(cv_image)
    font = ImageFont.truetype("arial.ttf", 24)

    draw.text((50, 50), f"Full Name: {data['full_name']}", fill="black", font=font)
    draw.text((50, 100), f"Age: {data['age']}", fill="black", font=font)
    draw.text((50, 150), f"Place: {data['place']}", fill="black", font=font)
    draw.text((50, 200), f"Graduate: {data['graduate']}", fill="black", font=font)
    draw.text((50, 250), f"Languages: {data['languages']}", fill="black", font=font)
    draw.text((50, 300), f"Skills: {data['skills']}", fill="black", font=font)
    draw.text((50, 350), f"Experiences: {data['experiences']}", fill="black", font=font)

    profile_img = Image.open(data['picture'])
    profile_img = profile_img.resize((150, 150))
    cv_image.paste(profile_img, (600, 50))

    cv_image_path = f"{chat_id}_cv.jpg"
    cv_image.save(cv_image_path)
    
    with open(cv_image_path, 'rb') as cv_file:
        bot.send_photo(chat_id, cv_file)
    
    # Clean up
    del user_data[chat_id]

bot.polling()