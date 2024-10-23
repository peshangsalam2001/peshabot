import telebot
import requests

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
OWM_API_KEY = 'f2305d59493db9a74c3809126c607b56'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me your location, and I'll provide the current weather update.")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    lat, lon = message.location.latitude, message.location.longitude
    weather = get_weather(lat, lon)
    bot.reply_to(message, weather)

def get_weather(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OWM_API_KEY}'
    response = requests.get(url).json()
    if response.get('main'):
        temp = response['main']['temp']
        desc = response['weather'][0]['description']
        return f"Current temperature: {temp}°C\nWeather: {desc.capitalize()}"
    else:
        return "Sorry, I couldn't fetch the weather data."

bot.polling()