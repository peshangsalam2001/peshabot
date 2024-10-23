import telebot
import os
from pydub import AudioSegment
import speech_recognition as sr

API_TOKEN = '7686120166:AAGnrPNFIHvgXdlL3G9inlouM3f7p7VZfkY'
bot = telebot.TeleBot(API_TOKEN)

# Path to store audio files
AUDIO_PATH = 'audio/'
if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)

# Initialize the recognizer
recognizer = sr.Recognizer()

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Download the voice file
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save the voice file
        audio_file = AUDIO_PATH + file_info.file_path.split('/')[-1] + '.ogg'
        with open(audio_file, 'wb') as f:
            f.write(downloaded_file)

        # Convert OGG file to WAV
        wav_file = audio_file.replace('.ogg', '.wav')
        audio = AudioSegment.from_ogg(audio_file)
        audio.export(wav_file, format='wav')

        # Use SpeechRecognition to convert audio to text
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ckb')
        
        # Send the text back to the user
        bot.reply_to(message, text)
        
        # Clean up the audio files
        os.remove(audio_file)
        os.remove(wav_file)
        
    except Exception as e:
        bot.reply_to(message, "Sorry, I couldn't process the audio.")
        print(e)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a voice message in Kurdish Sorani, and I will convert it to text.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Just send me a voice message in Kurdish Sorani, and I will convert it to text.")

bot.polling()