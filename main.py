import telebot
import requests

API_KEY = "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"
TELEGRAM_BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def ask_claude_via_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://your-app-name.com",  # دەتوانیت بگۆری بە ناوی سایتەکەت یان تۆمار نەکەیت
        "Content-Type": "application/json"
    }

    data = {
        "model": "anthropic/claude-3-opus",  # یان claude-3-sonnet بۆ خفیف‌تر
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    result = response.json()
    return result["choices"][0]["message"]["content"]

@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user_prompt = message.text
    bot.send_message(message.chat.id, "تکایە چاوەڕێ بکە... ڕاپۆرت لە Claude-3 دەنێرێت.")

    try:
        full_prompt = f"تکایە ڕاپۆرتێکی درێژ و تەکنیکی و جوان بنووسە بە زمانی کوردی سۆرانی لەسەر: {user_prompt}"
        answer = ask_claude_via_openrouter(full_prompt)
        bot.send_message(message.chat.id, answer)
    except Exception as e:
        bot.send_message(message.chat.id, f"هەڵەیەک ڕویدا: {e}")

bot.polling()