import time
import schedule
import requests
from datetime import datetime, timedelta
from translate import Translator
from telebot import TeleBot
from config import Bot_token, News_API_TOKEN

# Конфігурація
TELEGRAM_TOKEN = Bot_token
TELEGRAM_CHAT_ID = "@testcrupto"  # Ваш Telegram-канал/чат
NEWSAPI_URL = "https://newsapi.org/v2/everything"
NEWSAPI_KEY = News_API_TOKEN  # Ваш токен NewsAPI
bot = TeleBot(TELEGRAM_TOKEN)
translator = Translator(to_lang="ru")
published_urls = set()  # Збереження URL вже опублікованих новин

def get_crypto_news():
    """Отримання новин з NewsAPI"""
    params = {
        "q": "cryptocurrency OR bitcoin OR blockchain",  # Ключові слова для пошуку
        "sortBy": "publishedAt",  # Сортування за часом публікації
        "language": "en",  # Мова новин
        "apiKey": NEWSAPI_KEY
    }
    try:
        response = requests.get(NEWSAPI_URL, params=params)
        if response.status_code == 200:
            news = response.json().get("articles", [])
            print(f"Отримано новин: {len(news)}")
            return news
        else:
            print(f"Помилка отримання новин: {response.status_code}")
            return []
    except Exception as e:
        print(f"Помилка підключення до API: {e}")
        return []

def filter_recent_news(news_list):
    """Фільтрування новин за останню годину"""
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_news = []
    for news in news_list:
        if "publishedAt" in news:
            news_time = datetime.strptime(news["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
            if news_time > one_hour_ago:
                recent_news.append(news)
    return recent_news

def translate_text(text):
    """Переклад тексту на українську з обмеженням довжини"""
    try:
        if len(text) > 500:  # Обмеження довжини
            text = text[:500]
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Помилка перекладу: {e}")
        return text  # Повертаємо оригінальний текст у разі помилки

def post_news_to_telegram():
    """Публікація новин у Telegram"""
    news_list = get_crypto_news()  # Отримання всіх новин
    if not news_list:
        print("Немає новин для обробки.")
        return

    recent_news = filter_recent_news(news_list)  # Фільтрування за останню годину
    recent_news = [news for news in recent_news if news.get("url") not in published_urls]  # Уникнення повторів

    if not recent_news:
        print("Немає нових новин за останню годину.")
        return

    for news in recent_news[:5]:  # Публікуємо максимум 5 новин
        url = news.get("url", "Без посилання")
        title = translate_text(news.get("title", "Без назви"))
        description = translate_text(news.get("body", "Опис недоступний"))
        message = f"📰 {title}\n\n{description[:500]}...\n\n🔗 [Читати далі]({url})"
        try:
            time.sleep(2)  # Затримка між повідомленнями
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
            published_urls.add(url)  # Уникнення дублювання
            print(f"Опубліковано: {title}")
        except Exception as e:
            print(f"Помилка надсилання: {e}")

# Розклад роботи
schedule.every(15).hours.do(post_news_to_telegram)

if __name__ == "__main__":
    print("Бот запущено. Очікування...")
    post_news_to_telegram()
    while True:
        schedule.run_pending()
        time.sleep(1)
