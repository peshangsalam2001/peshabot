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
BOT_TOKEN = "8072279299:AAHAEodRhWpDb2g7EIVNFc3pk1Yg0YlpaPc"
bot = telebot.TeleBot(BOT_TOKEN)

# Pet Notify Specific Information
PETNOTIFY_BASE_URL = "https://app.petnotify.com"
STRIPE_API_URL = "https://api.stripe.com/v1/tokens"

# Headers (Common ones, specific ones will be added in functions)
COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2  Mobile/15E148 Safari/605.1.15",
    "Origin": "https://app.petnotify.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Connection": "keep-alive",
}

def create_temp_user(first_name, last_name, email):
    url = f"{PETNOTIFY_BASE_URL}/api/signup/temp-user"
    headers = COMMON_HEADERS.copy()
    headers["Content-Type"] = "application/json"
    headers["Referer"] = "https://app.petnotify.com/signup/premium?plan=yearly"
    payload = json.dumps({"data": {"sendNewsAndUpdates": True, "firstName": first_name, "lastName": last_name, "email": email, "confirmEmail": email, "promoCode": None, "plan": "year"}})
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating temp user: {e} - Response: {response.text}")
        return None

def get_signup_breakdown():
    url = f"{PETNOTIFY_BASE_URL}/api/signup/breakdown"
    headers = COMMON_HEADERS.copy()
    headers["Content-Type"] = "application/json"
    headers["Referer"] = "https://app.petnotify.com/signup/premium/payment"
    payload = json.dumps({"data": {"user": {"firstName": "Master", "lastName": "Lord", "email": "peshangsalam2001@gmail.com", "sendNewsAndUpdates": True}, "plan": "year", "intellitags": [{"size": "small", "maxCharacters": 12, "type": "Cat", "error": None, "weight": "50", "name": "Jack", "nameOnTag": "KURD", "nameTooLong": False}], "shippingAddress": {"country": "US", "state": "NJ", "address": "198 White Horse Pike", "city": "West Collingswood", "zip": "08107", "phone": "314-729-3729"}, "promoCode": None, "subscriptionPlan": "year"}})
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting signup breakdown: {e} - Response: {response.text}")
        return None

def create_stripe_token(cc, mm, yy, cvv, name, email):
    headers = COMMON_HEADERS.copy()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Origin"] = "https://js.stripe.com"
    headers["Referer"] = "https://js.stripe.com/"
    payload = f"card[number]={cc}&card[exp_month]={mm}&card[exp_year]={yy}&card[cvc]={cvv}&card[name]={name}&email={email}&key=pk_live_51Jj45g2E5nO44xT2ex69s3j5hcc4v24K61lVn9sQ474m4W819079R5s95i85349612015"
    try:
        response = requests.post(STRIPE_API_URL, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get("id")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating Stripe token: {e} - Response: {response.text}")
        return None

# --- Part 1 Ends Here ---
# --- Part 2 Begins Here ---

def finalize_signup(stripe_token):
    url = f"{PETNOTIFY_BASE_URL}/api/signup"
    headers = COMMON_HEADERS.copy()
    headers["Content-Type"] = "application/json"
    headers["Referer"] = "https://app.petnotify.com/signup/premium/payment"
    payload = json.dumps({"data": {"token": stripe_token, "promoCode": None, "redemptionCode": None, "isAnnualPlan": False, "stripeSubscriptionPlan": "price_1HLK1bBiYf8zs0JGiKROzUcG", "policyAcceptance": True, "smsPermission": True, "intellitags": [{"size": "small", "maxCharacters": 12, "type": "Cat", "error": None, "weight": "50", "name": "Jack", "nameOnTag": "KURD", "nameTooLong": False}], "shippingAddress": {"country": "US", "state": "NJ", "address": "198 White Horse Pike", "city": "West Collingswood", "zip": "08107", "phone": "314-729-3729"}}})
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error finalizing signup: {e} - Response: {response.text}")
        return None

# Telegram Bot Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Let's sign up for Pet Notify. Please provide your first name, last name, and email (separated by spaces):")

@bot.message_handler(func=lambda message: len(message.text.split()) == 3)
def get_user_info(message):
    first_name, last_name, email = message.text.split()
    bot.reply_to(message, f"Creating temporary user for {email}...")
    temp_user_data = create_temp_user(first_name, last_name, email)
    if temp_user_data:
        bot.reply_to(message, "Temporary user created. Now processing signup breakdown...")
        breakdown_data = get_signup_breakdown()
        if breakdown_data:
            bot.reply_to(message, "Signup breakdown received. Please provide your credit card details in the format: cc|mm|yy|cvv")
        else:
            bot.reply_to(message, "Failed to get signup breakdown.")
    else:
        bot.reply_to(message, "Failed to create temporary user.")

@bot.message_handler(func=lambda message: len(message.text.split('|')) == 4)
def process_payment_info(message):
    try:
        cc, mm_str, yy_str, cvv = message.text.split('|')

        if not (mm_str.isdigit() and yy_str.isdigit() and cvv.isdigit()):
            bot.reply_to(message, "Invalid month, year, or CVV. Please use numbers.")
            return

        mm = int(mm_str)
        yy = int(yy_str) if len(yy_str) == 4 else int(f"20{yy_str}")

        bot.reply_to(message, "Creating Stripe token...")
        stripe_token = create_stripe_token(cc, mm, yy, cvv, "Master Lord", "peshangsalam2001@gmail.com") # Using static name/email from example
        if stripe_token:
            bot.reply_to(message, f"Stripe Token created: {stripe_token}. Finalizing signup...")
            signup_result = finalize_signup(stripe_token)
            if signup_result:
                bot.reply_to(message, f"Signup successful!\n{json.dumps(signup_result, indent=2)}")
            else:
                bot.reply_to(message, "Failed to finalize signup.")
        else:
            bot.reply_to(message, "Failed to create Stripe token. Card might be invalid.")

    except ValueError:
        bot.reply_to(message, "Invalid input format. Please use: cc|mm|yy|cvv")
    except Exception as e:
        logging.error(f"Error processing card input: {e}")
        bot.reply_to(message, f"An error occurred: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I can help you sign up for Pet Notify. Send /start to begin.")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)