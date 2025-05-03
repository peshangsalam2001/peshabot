import telebot
import requests
from bs4 import BeautifulSoup
import urllib.parse

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

def extract_text_between_markers(text, start_marker, end_marker):
    start_index = text.find(start_marker)
    if start_index == -1:
        return None
    start_index += len(start_marker)
    end_index = text.find(end_marker, start_index)
    if end_index == -1:
        return None
    return text[start_index:end_index].strip()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    topic = message.text.strip()
    # Encode the topic to be URL-safe
    query = urllib.parse.quote(topic)

    # Construct the URL to search or get the answer page
    # NOTE: Replace this URL with the actual search or query URL of your site
    # Example (you need to adjust this based on your site’s structure):
    url = f"https://zaniary.com/search?q={query}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first blog post link or direct content div
        # This depends on your website’s structure.
        # For example, if search returns a list of results, get the first result URL:
        first_result = soup.find('a', class_='post-title')  # Adjust selector as needed
        if first_result and first_result['href']:
            article_url = urllib.parse.urljoin(url, first_result['href'])
        else:
            # If no search results, maybe the search page itself contains the content?
            article_url = url

        # Fetch the article page
        article_resp = requests.get(article_url)
        article_resp.raise_for_status()

        article_soup = BeautifulSoup(article_resp.text, 'html.parser')
        content_div = article_soup.find('div', class_='js_blog_content')

        if not content_div:
            bot.reply_to(message, "Sorry, could not find the content on the page.")
            return

        full_text = content_div.get_text(separator='\n', strip=True)
        extracted_text = extract_text_between_markers(full_text, "ناوه‌ڕۆك", "سەرچاوەکان")

        if extracted_text:
            if len(extracted_text) > 4000:
                extracted_text = extracted_text[:4000] + "\n\n...[truncated]"
            bot.reply_to(message, extracted_text)
        else:
            bot.reply_to(message, "Sorry, could not find the text between 'ناوه‌ڕۆك' and 'سەرچاوەکان'.")
    except Exception as e:
        bot.reply_to(message, f"Error fetching data: {e}")

bot.polling()
