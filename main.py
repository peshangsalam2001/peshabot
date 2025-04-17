import telebot
from PIL import Image, ImageDraw, ImageFont
API_KEY = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
bot = telebot.TeleBot(API_KEY)

user_data = {}
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    bot.send_message(user_id, "Welcome! Let's create your CV. Please send me your profile picture.")

def ask_next_info(user_id, message, next_info, question):
    user_data[user_id][next_info] = message.text
    bot.send_message(user_id, question)

@bot.message_handler(content_types=['photo', 'text'])
def collect_info(message):
    user_id = message.from_user.id
    user_info = user_data.get(user_id, {})

    if 'profile_pic' not in user_info and message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f"{user_id}_profile_pic.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        user_data[user_id]['profile_pic'] = f"{user_id}_profile_pic.jpg"
        bot.send_message(user_id, "What is your full name?")
    elif 'name' not in user_info:
        ask_next_info(user_id, message, 'name', "What is your phone number?")
    elif 'phone' not in user_info:
        ask_next_info(user_id, message, 'phone', "What is your email address?")
    elif 'email' not in user_info:
        ask_next_info(user_id, message, 'email', "What is your education?")
    elif 'education' not in user_info:
        ask_next_info(user_id, message, 'education', "What is your work experience?")
    elif 'experience' not in user_info:
        ask_next_info(user_id, message, 'experience', "What are your skills?")
    elif 'skills' not in user_info:
        user_info['skills'] = message.text
        create_and_send_cv(user_id)

def create_and_send_cv(user_id):
    user_info = user_data[user_id]
    
   
    img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
   
    font_large = ImageFont.truetype("arial.ttf", 36)
    font_medium = ImageFont.truetype("arial.ttf", 24)
    font_small = ImageFont.truetype("arial.ttf", 18)
    
  
    profile_pic = Image.open(user_info['profile_pic']).resize((150, 150))
    img.paste(profile_pic, (325, 20))
    
 
    d.text((50, 200), f"Name: {user_info['name']}", fill=(0, 0, 0), font=font_large)
    d.text((50, 250), f"Phone: {user_info['phone']}", fill=(0, 0, 0), font=font_medium)
    d.text((50, 290), f"Email: {user_info['email']}", fill=(0, 0, 0), font=font_medium)
    d.text((50, 330), f"Education: {user_info['education']}", fill=(0, 0, 0), font=font_medium)
    d.text((50, 370), f"Experience: {user_info['experience']}", fill=(0, 0, 0), font=font_medium)
    d.text((50, 410), f"Skills: {user_info['skills']}", fill=(0, 0, 0), font=font_medium)
    

    img_path = f"{user_id}_cv.png"
    img.save(img_path)
    

    with open(img_path, 'rb') as img_file:
        bot.send_photo(user_id, img_file)

    del user_data[user_id]

bot.polling()
