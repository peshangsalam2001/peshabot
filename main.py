import telebot
import threading
import time
from datetime import datetime

API_KEY = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_KEY)

reminders = []

def check_reminders():
    while True:
        now = datetime.now()
        to_remove = []
        for reminder in reminders:
            if now >= reminder['time']:
                bot.send_message(reminder['chat_id'], f"Reminder: {reminder['text']}")
                to_remove.append(reminder)
        for reminder in to_remove:
            reminders.remove(reminder)
        time.sleep(60)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Use /setreminder command to set a reminder. Format: /setreminder YYYY-MM-DD HH:MM Task")

@bot.message_handler(commands=['setreminder'])
def set_reminder(message):
    try:
        command = message.text.split(' ', 2)
        if len(command) < 3:
            raise ValueError("Invalid format")
        
        date_str, time_str, text = command[1], command[2], command[3]
        reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        reminders.append({
            'chat_id': message.chat.id,
            'time': reminder_time,
            'text': text
        })
        
        bot.reply_to(message, f"Reminder set for {reminder_time}")
    except Exception as e:
        bot.reply_to(message, f"Failed to set reminder. Use format: /setreminder YYYY-MM-DD HH:MM Task\nError: {e}")

threading.Thread(target=check_reminders, daemon=True).start()
bot.polling()