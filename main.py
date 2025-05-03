import telebot
import requests
from bs4 import BeautifulSoup
import urllib.parse

BOT_TOKEN = "7018443911:AAFP7YgMlc03URuqMUv-_VzysmewC0vt8jM"
bot = telebot.TeleBot(BOT_TOKEN)

def search_topic_and_get_url(topic):
    # Encode topic for URL
    query = urllib.parse.quote(topic)
    search_url = f"https://zaniary.com/blog?search={query}"
    resp = requests.get(search_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Find the first article link in the search result
    # Adjust selector if needed based on actual HTML structure
    first_link = soup.select_one('a.blog-title, a.post-title, a[href^="/blog/"]')
    if first_link and first_link.get('href'):
        article_url = urllib.parse.urljoin(search_url, first_link['href'])
        return article_url
    return None

def extract_answer_from_article(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Use the selector you provided
    answer_p = soup.select_one('#mw-content-text > div.js_blog_content > p:nth-child(2)')
    if answer_p:
        return answer_p.get_text(strip=True)
    return None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    topic = message.text.strip()
    try:
        article_url = search_topic_and_get_url(topic)
        if not article_url:
            bot.reply_to(message, "Sorry, I couldn't find any article for your topic.")
            return

        answer = extract_answer_from_article(article_url)
        if answer:
            # Telegram message limit is 4096 characters
            if len(answer) > 4000:
                answer = answer[:4000] + "\n\n...[truncated]"
            bot.reply_to(message, answer)
        else:
            bot.reply_to(message, "Sorry, I couldn't find an answer in the article.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

bot.polling()
