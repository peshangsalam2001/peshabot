import telebot
import requests
import random
import string
import time
import json

BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_51Jhet4HYghhmd4CamObYqu2qaPmZlp3SqgYcBfUbKrgBBnS040UHuHvzuHxl7I4GQwFXEwjAx62BQu01Q76BRmum00dZ72P1K2"
STRIPE_URL = "https://api.stripe.com/v1/tokens"

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
    return cc, mm.zfill(2), yy, cvc

def get_stripe_token(cc, mm, yy, cvc):
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
        "key": STRIPE_PUBLISHABLE_KEY
    }
    resp = requests.post(STRIPE_URL, data=data, headers=headers)
    try:
        resp_json = resp.json()
    except Exception as e:
        return None, None, f"Stripe JSON decode error: {str(e)}"
    token = resp_json.get('id')
    return token, resp_json, None

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 Stripe Token Checker Bot\n"
        "Send one or multiple cards (each on a new line) in the format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n\n"
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
        token, resp_json, err = get_stripe_token(cc, mm, yy, cvc)
        if err:
            bot.send_message(message.chat.id, f"❌ Error: {err}")
        else:
            bot.send_message(message.chat.id, f"Card: {cc}|{mm}|{yy}|{cvc}\nStripe Token: {token if token else 'Not found'}")
            # Send full JSON response (pretty-printed)
            bot.send_message(message.chat.id, f"Full Stripe Response:\n<pre>{json.dumps(resp_json, indent=2)}</pre>", parse_mode="HTML")
        time.sleep(10)  # 10-second delay between cards

bot.infinity_polling()