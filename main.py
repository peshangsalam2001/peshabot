import telebot
import requests
from bs4 import BeautifulSoup
import urllib.parse

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

def search_and_extract_info(topic):
    # Encode topic for URL
    query = urllib.parse.quote(topic)
    search_url = f"https://zaniary.com/blogs?search={query}"

    response = requests.get(search_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all blog entries in search results
    # Inspect the page to find the container for each blog post summary
    # Based on your example, let's assume each post is inside a div with class 'blog-entry' or similar
    # You need to adjust the selector based on actual HTML structure of search results
    posts = soup.select('div.blog-entry, div.blog-post, div.post')  # Try these selectors, adjust if needed

    if not posts:
        # If no posts found with above selectors, fallback: try to get all content under main container
        main_content = soup.select_one('div#main-content, div.content, div.blog-list')
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
            if text:
                return text
        return None

    # Extract text from each post summary and join them
    all_texts = []
    for post in posts:
        # Extract all text inside each post block
        text = post.get_text(separator='\n', strip=True)
        if text:
            all_texts.append(text)

    if all_texts:
        return "\n\n---\n\n".join(all_texts)
    else:
        return None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    topic = message.text.strip()
    try:
        info = search_and_extract_info(topic)
        if info:
            # Telegram message limit is 4096 characters
            if len(info) > 4000:
                info = info[:4000] + "\n\n...[truncated]"
            bot.reply_to(message, info)
        else:
            bot.reply_to(message, "Sorry, I couldn't find any information on that topic.")
    except Exception as e:
        bot.reply_to(message, f"Error occurred: {e}")

bot.polling()
