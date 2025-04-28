import telebot
import requests
import json
import logging
import random
import string
import time
import re  # For extracting CSRF token

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your actual Telegram Bot Token
BOT_TOKEN = "8072279299:AAHAEodRhWpDb2g7EIVNFc3pk1Yg0YlpaPc"
bot = telebot.TeleBot(BOT_TOKEN)

# Kajabi Specific Information
KAJABI_BASE_URL = "https://app.kajabi.com"
STRIPE_API_URL = "https://api.stripe.com/v1/payment_methods"

# Headers (Common ones, specific ones will be added in functions)
COMMON_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "origin": "https://js.stripe.com",
    "sec-fetch-dest": "empty",
}

KAJABI_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "origin": "https://app.kajabi.com",
    "sec-fetch-dest": "empty",
    "content-type": "application/json",
    "referer": "https://app.kajabi.com/signup/kajabi_pro_monthly?signup_source=spring_promo_2025&marketing_form_name=start_your_trial_form",
}

# Cookies
COOKIES = {
    "AWSALBTG": "BybjASeB357nDAmp0JFm9iyr7K2YE5bSN/veQnrDSVEa1MrfPEMzKRjIrtt4mEh6qCLfN9F/KHsc56VPep6Kt9O7FWB8iQGzDoGuTZ5KZKzL2VTaTuDucq8Zz0XJKeosdNgOE8VrkryTn0qNw3xmlDffidLBWOCxOcucYbmPWPq5",
    "AWSALBTGCORS": "BybjASeB357nDAmp0JFm9iyr7K2YE5bSN/veQnrDSVEa1MrfPEMzKRjIrtt4mEh6qCLfN9F/KHsc56VPep6Kt9O7FWB8iQGzDoGuTZ5KZKzL2VTaTuDucq8Zz0XJKeosdNgOE8VrkryTn0qNw3xmlDffidLBWOCxOcucYbmPWPq5",
    "_csrf_token": "",  # Will be fetched dynamically
    "_kjb_session": "f4b46a04a3446335b558a12ec5cd994c",
    "_dd_s": "rum=2&id=26894acf-6058-4cbe-aeb3-fb6fe008d8e5&created=1745853378533&expire=1745854478794",
    "_fbp": "fb.1.1738294343522.299726064264604019",
    "__stripe_mid": "d9a4285f-56f1-4d5b-acdb-56fd4cdd865c5fd491",
    "__stripe_sid": "8f6e8445-ccaf-4136-84ef-093db5757517b55381",
    "_clsk": "ec9eef%7C1745853546797%7C3%7C1%7Ci.clarity.ms%2Fcollect",
    "_pin_unauth": "dWlkPU1qZG1OVGhtWkdFdFlUVmlaUzAwWWpBNUxXSm1Zek10T0dVeE9XUmpORFJqTlRJMA",
    "_uetsid": "ae1f09e0244311f08a3b4f414acae39f",
    "_uetvid": "fc20ba60df8311efaad5ed321a04f772",
    "_kjb_ua_components": "c500920e82e6f7c28ebe0322d81c4e35",
    "_ga": "GA1.1.379627536.1738294343",
    "_ga_4XSF0VL22B": "GS1.1.1745853354.3.1.1745853514.60.0.344046606",
    "_gcl_au": "1.1.652603712.1738294343",
    "_rdt_uuid": "1738294343470.741f1f7d-7911-4fa3-9e52-53764bc2ddcf",
    "__cf_bm": "iyhtb68MyF7PQYGZQk4p9lXStqdP0qaiKP3vnspmrYQ-1745853447-1.0.1.1-.xsdUGfPkh_dB2Uwu4Br.LbanzpB1mzBL_Q5WV4rOxvK_XL1GePZPohuCyp9HRvV73JuJ1MPGw2cOv3Rfif9jrLsGROahYY2CU.5MnbWRq7XQg6vc9WmggjcFBTI9461",
    "rl_anonymous_id": "RS_ENC_v3_IjEzZTg3Y2Y0LTRkOTQtNGMxOC1hMTcwLTMyZDZmOGNjMTg5YiI%3D",
    "rl_page_init_referrer": "RS_ENC_v3_Imh0dHBzOi8vd3d3Lmdvb2dsZS5jb20vIg%3D%3D",
    "rl_page_init_referring_domain": "RS_ENC_v3_Ind3dy5nb29nbGUuY29tIg%3D%3D",
    "rl_session": "RS_ENC_v3_eyJpZCI6MTc0NTg1MzM1MzM1MywiZXhwaXJlc0F0IjoxNzQ1ODU1MjQ3ODYxLCJzZXNzaW9uU3RhcnQiOmZhbHNlLCJhdXRvVHJhY2siOnRydWUsInRpbWVvdXQiOjE4MDAwMDB9",
    "kjb_signup_id": "eb5a9923-d42b-4925-8ec2-6f6ba805c790",
    "_clck": "len4ba%7C2%7Cfvg%7C0%7C1944",
    "amp_d4cd2a": "3kZYsXWKL2G2J_ZYNQEFeB...1ipufg4ir.1ipufg4ir.0.0.0",
    "_cfuvid": "fcnQgtS5OEQfPjSz9cOlvyVa7i6yhk.0J4FehW6X6Lo-1745853352809-0.0.1.1-604800000",
    "_tt_enable_cookie": "1",
    "_ttp": "2lfEWa5Q5yMg89yPHyTAdNaQLoa.tt.1",
}

def get_signup_page():
    url = f"{KAJABI_BASE_URL}/signup/kajabi_pro_monthly"
    headers = KAJABI_HEADERS.copy()
    headers.pop("content-type", None) # Not needed for GET request
    try:
        response = requests.get(url, headers=headers, cookies=COOKIES)
        response.raise_for_status()
        return response.text, response.cookies
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting signup page: {e} - Response: {response.text}")
        return None, None

def extract_csrf_token(html_content):
    match = re.search(r'<meta name="csrf-token" content="([^"]+)">', html_content)
    if match:
        return match.group(1)
    return None

def create_payment_method(cc, mm, yy, cvv, postal_code, guid):
    headers = COMMON_HEADERS.copy()
    headers["content-type"] = "application/x-www-form-urlencoded"
    payload = f"type=card&billing_details[address][postal_code]={postal_code}&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&guid={guid}&muid={COOKIES.get('__stripe_mid', '')}&sid={COOKIES.get('__stripe_sid', '')}&pasted_fields=number&payment_user_agent=stripe.js%2Fb85ba7b837%3B+stripe-js-v3%2Fb85ba7b837%3B+card-element&referrer=https%3A%2F%2Fapp.kajabi.com&time_on_page=62482&key=pk_live_GM2gUsVfs3fY1xot5C7WDhBP"
    try:
        response = requests.post(STRIPE_API_URL, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get("id")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating payment method: {e} - Response: {response.text}")
        return None

# --- Part 1 Ends Here ---
# --- Part 2 Begins Here ---

def submit_signup_form(payment_method_id, email, first_name, last_name, password, postal_code, csrf_token):
    url = f"{KAJABI_BASE_URL}/signup/kajabi_pro_monthly"
    headers = KAJABI_HEADERS.copy()
    headers["x-csrf-token"] = csrf_token
    payload = json.dumps({
        "accounts_signup": {
            "signup_country": "US",
            "signup_ip_address": "176.222.63.108",
            "time_zone": "Asia/Baghdad",
            "payment_type": "credit_card",
            "coupon_id": None,
            "email": email,
            "first_name": first_name,
            "invitation_code": None,
            "last_name": last_name,
            "request_url": "https://app.kajabi.com/signup/kajabi_pro_monthly?signup_source=spring_promo_2025&marketing_form_name=start_your_trial_form",
            "signup_source": "spring_promo_2025",
            "password": password,
            "password_confirmation": password,
            "postal_code": postal_code,
            "payment_method_id": payment_method_id
        }
    })
    try:
        response = requests.post(url, headers=headers, data=payload, cookies=COOKIES)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error submitting signup form: {e} - Response: {response.text}")
        return None

# Telegram Bot Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Let's sign up for Kajabi. Please provide your email, first name, last name, and desired password (separated by spaces):")

@bot.message_handler(func=lambda message: len(message.text.split()) == 4)
def get_user_info(message):
    global signup_html_content, kajabi_cookies
    email, first_name, last_name, password = message.text.split()
    bot.reply_to(message, "Fetching signup page to get CSRF token...")
    signup_html_content, kajabi_cookies = get_signup_page()
    if signup_html_content:
        csrf_token = extract_csrf_token(signup_html_content)
        if csrf_token:
            COOKIES["_csrf_token"] = csrf_token
            bot.reply_to(message, "CSRF token obtained. Please provide your credit card details in the format: cc|mm|yy|cvv|postal_code|guid")
        else:
            bot.reply_to(message, "Error: Could not extract CSRF token.")
    else:
        bot.reply_to(message, "Error: Could not fetch signup page.")

@bot.message_handler(func=lambda message: len(message.text.split('|')) == 6)
def process_payment_info(message):
    try:
        cc, mm_str, yy_str, cvv, postal_code, guid = message.text.split('|')

        if not (mm_str.isdigit() and yy_str.isdigit() and cvv.isdigit() and postal_code.isdigit() and len(guid) > 0):
            bot.reply_to(message, "Invalid format. Please use numbers for month, year, CVV, postal code, and provide a valid GUID.")
            return

        mm = int(mm_str)
        yy = int(yy_str) if len(yy_str) == 4 else int(f"20{yy_str}")

        bot.reply_to(message, "Creating payment method...")
        payment_method_id = create_payment_method(cc, mm, yy, cvv, postal_code, guid)

        if payment_method_id:
            bot.reply_to(message, f"Payment method created: {payment_method_id}. Submitting signup form...")

            user_info = message.text.split()[:4] # Reuse info from previous step
            email, first_name, last_name, password = user_info[0], user_info[1], user_info[2], user_info[3]

            csrf_token = COOKIES.get("_csrf_token")
            if not csrf_token:
                bot.reply_to(message, "Error: CSRF token is missing.")
                return

            signup_result = submit_signup_form(payment_method_id, email, first_name, last_name, password, postal_code, csrf_token)
            if signup_result:
                bot.reply_to(message, f"Signup successful!\n{json.dumps(signup_result, indent=2)}")
            else:
                bot.reply_to(message, "Failed to submit signup form.")
        else:
            bot.reply_to(message, "Failed to create payment method. Card might be invalid.")

    except ValueError:
        bot.reply_to(message, "Invalid input format. Please use: cc|mm|yy|cvv|postal_code|guid")
    except Exception as e:
        logging.error(f"Error processing payment info: {e}")
        bot.reply_to(message, f"An error occurred: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I can help you sign up for Kajabi. Send /start to begin.")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)
