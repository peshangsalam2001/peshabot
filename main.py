import telebot
import colorsys
import matplotlib.colors as mcolors

BOT_TOKEN = '7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI'
bot = telebot.TeleBot(BOT_TOKEN)

def hex_to_rgb(hex_color):
    return mcolors.to_rgb(hex_color)

def rgb_to_hex(rgb):
    return mcolors.to_hex(rgb)

def get_complementary_colors(color):
    try:
        rgb = hex_to_rgb(color)
    except:
        return None

    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(*rgb)

    # Generate complementary and analogous colors
    combos = []
    for delta in [0.5, -0.08, 0.08, -0.16, 0.16]:  # Complementary + analogs
        new_h = (h + delta) % 1.0
        new_rgb = colorsys.hls_to_rgb(new_h, l, s)
        combos.append(rgb_to_hex(new_rgb))
    return combos

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎨 Send me a color name (like `red`) or hex code (like `#1abc9c`) and I’ll suggest matching colors!")

@bot.message_handler(func=lambda msg: True)
def color_handler(message):
    user_color = message.text.strip().lower()
    colors = get_complementary_colors(user_color)

    if colors:
        reply = f"🌈 Color matches for `{user_color}`:\n\n"
        for i, c in enumerate(colors):
            reply += f"{i+1}. `{c}`\n"
        bot.send_message(message.chat.id, reply, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚠️ Please send a valid color name or hex code.")

bot.polling()
