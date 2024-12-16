import numpy as np
import pandas as pd
import time as tm
import logging
import re
from datetime import datetime, timedelta
from telebot import TeleBot
from config import API_KEY, API_SECRET, Bot_token, COINGECKO_API_TOKEN
import ccxt
import requests
import nltk
nltk.download('punkt')
# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API ключі
api_key = API_KEY
api_secret = API_SECRET
TELEGRAM_TOKEN = Bot_token
TELEGRAM_CHAT_ID = "@testcrupto"
bot = TeleBot(TELEGRAM_TOKEN)

# Підключення до Binance
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
})

# API для новин (наприклад, CryptoPanic)
NEWS_API_URL = "https://cryptopanic.com/api/v1/posts/"
NEWS_API_KEY = COINGECKO_API_TOKEN


def fetch_news(symbol):
    """Отримує новини по символу"""
    try:
        # Надсилання запиту до API
        response = requests.get(
            NEWS_API_URL,
            params={
                "auth_token": NEWS_API_KEY,
                "currencies": symbol.split('/')[0].lower(),
                "public": "true",
            }
        )

        # Перетворення відповіді у формат JSON
        news_data = response.json()

        # Перевірка наявності результатів
        if 'results' not in news_data:
            logging.error("Відповідь API не містить поля 'results'")
            return []

        # Фільтрація новин, які стосуються символу
        relevant_news = [
            item for item in news_data['results']
            if symbol.split('/')[0].lower() in (item.get('currencies') or [])
        ]

        logging.info(f"Отримано {len(relevant_news)} релевантних новин для {symbol}")
        return relevant_news

    except requests.exceptions.RequestException as e:
        logging.error(f"Помилка запиту до API: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Невідома помилка при отриманні новин: {str(e)}")
        return []

def clean_text(text):
    """Очищує текст новини від зайвих символів"""
    try:
        # Видалення посилань, HTML-тегів, зайвих символів
        text = re.sub(r"http\S+|www\S+", "", text)  # Видалення URL
        text = re.sub(r"<.*?>", "", text)  # Видалення HTML-тегів
        text = re.sub(r"[^a-zA-Z0-9 .,!?\-]", "", text)  # Видалення всіх незвичайних символів
        return text.strip()
    except Exception as e:
        logging.error(f"Помилка очищення тексту: {str(e)}")
        return text


# Розширені словники позитивних і негативних слів на трьох мовах
positive_words = [
    'добрий', 'щасливий', 'радісний', 'прекрасний', 'чудовий', 'відмінно', 'чудовий', 'гарний',
    'позитивний', 'успішний', 'веселий', 'кращий', 'класний', 'чудово', 'спокійний', 'сміливий',
    'енергійний', 'високий', 'професійний', 'люблячий', 'гордий', 'піднесений', 'міцний', 'вдячний',
    'пристосований', 'благополучний', 'сильний', 'здоровий', 'вірний', 'щаслива', 'молодий',
    'цікаво', 'поважний', 'дружелюбний', 'креативний', 'вірний'
]

negative_words = [
    'поганий', 'сумний', 'нещасний', 'жахливий', 'страшний', 'негативний', 'погано', 'поганий',
    'несприятливий', 'трудний', 'прикрий', 'депресивний', 'невдачний', 'слабкий', 'хворий',
    'недобрий', 'непрофесійний', 'гіркий', 'неуспішний', 'пригнічений', 'відчужений', 'підступний',
    'грубий', 'злий', 'заздрісний', 'недружній', 'пригнічений', 'невдоволений', 'нещаслива',
    'мучений', 'неприємний', 'погано', 'різкий', 'зневажливий', 'жалюгідний', 'кривдити', 'нервовий',
    'апатичний', 'невірний'
]

# Додатково для англійської мови
positive_words_en = [
    'good', 'happy', 'joyful', 'wonderful', 'excellent', 'great', 'positive', 'successful', 'cheerful',
    'best', 'amazing', 'awesome', 'kind', 'friendly', 'loving', 'strong', 'healthy', 'energetic', 'creative',
    'motivated', 'grateful', 'thankful', 'bright', 'hopeful', 'optimistic', 'trustworthy', 'brave', 'peaceful'
]

negative_words_en = [
    'bad', 'sad', 'unhappy', 'horrible', 'awful', 'terrible', 'negative', 'unpleasant', 'depressing',
    'failure', 'weak', 'sick', 'angry', 'mean', 'rude', 'jealous', 'disappointed', 'hopeless', 'helpless',
    'unlucky', 'hurt', 'cruel', 'difficult', 'stressful', 'unpleasant', 'angry', 'frustrated', 'toxic',
    'toxic', 'nasty'
]

# Для російської мови
positive_words_ru = [
    'добрый', 'счастливый', 'радостный', 'прекрасный', 'чудесный', 'отличный', 'позитивный', 'успешный',
    'веселый', 'лучший', 'классный', 'спокойный', 'смелый', 'энергичный', 'профессиональный', 'любящий',
    'гордый', 'вдохновленный', 'крепкий', 'благополучный', 'сильный', 'здоровый', 'верный', 'счастливый',
    'молодой', 'интересный', 'уважаемый', 'дружелюбный', 'креативный'
]

negative_words_ru = [
    'плохой', 'грустный', 'несчастный', 'ужасный', 'страшный', 'негативный', 'плохо', 'плохой', 'неудачный',
    'приглушенный', 'депрессивный', 'несчастливый', 'слабый', 'больной', 'недобрый', 'непрофессиональный',
    'горький', 'неуспешный', 'приглушенный', 'неудовлетворенный', 'недружелюбный', 'пригнобленный', 'плохой',
    'разочарованный', 'неспокойный', 'нервный', 'апатичный', 'невезучий'
]

# Загальний список всіх слів
all_positive_words = positive_words + positive_words_en + positive_words_ru
all_negative_words = negative_words + negative_words_en + negative_words_ru

# Функція для аналізу емоційного забарвлення
def analyze_sentiment_text(text):
    """Функція для аналізу емоційного забарвлення тексту."""
    words = text.lower().split()

    # Лічильники для позитивних і негативних слів
    positive_count = sum(1 for word in words if word in all_positive_words)
    negative_count = sum(1 for word in words if word in all_negative_words)

    # Обчислення емоційного забарвлення
    sentiment_score = positive_count - negative_count
    return sentiment_score

def analyze_sentiment(news):
    """Аналізує емоційне забарвлення новин"""
    try:
        if not news:
            return None

        sentiments = []
        for item in news:
            # Об'єднання заголовка і тексту новини
            text = f"{item.get('title', '')} {item.get('body', '')}"

            # Очищення тексту
            clean_news = clean_text(text)

            # Аналіз емоційного забарвлення
            sentiment_score = analyze_sentiment_text(clean_news)
            sentiments.append(sentiment_score)

        # Обчислення середнього настрою
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        # Класифікація настрою
        if avg_sentiment > 0.1:
            return True  # Позитивний настрій
        elif avg_sentiment < -0.1:
            return False  # Негативний настрій
        else:
            return None  # Нейтральний настрій

    except Exception as e:
        logging.error(f"Помилка аналізу настрою: {str(e)}")
        return None

def analyze_news_impact(symbol):
    """Аналізує новини та вплив на ціну монети"""
    try:
        # Отримання новин
        news = fetch_news(symbol)

        if not news:
            logging.info(f"Новини для символу {symbol} не знайдено")
            return None

        # Аналіз настрою
        sentiment_score = analyze_sentiment(news)

        # Якщо настрій слабкий, не аналізуємо далі
        if sentiment_score is None:
            logging.info("Настрій нейтральний або недостатньо даних для аналізу")
            return None

        # Отримання зміни ціни за останню годину
        start_time = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
        price_change = get_price_change(symbol, start_time)

        # Аналіз впливу
        if sentiment_score and price_change > 0:
            logging.info("Позитивні новини підтверджують зростання ціни")
            return True
        elif not sentiment_score and price_change < 0:
            logging.info("Негативні новини підтверджують падіння ціни")
            return False
        else:
            logging.info("Настрій новин і зміна ціни не збігаються")
            return None

    except Exception as e:
        logging.error(f"Помилка аналізу впливу новин: {str(e)}")
        return None

def get_price_change(symbol, start_time):
    """Отримує зміну ціни за годину після стартового часу"""
    df = exchange.fetch_ohlcv(symbol, '1m', since=start_time)
    prices = pd.DataFrame(df, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Перевірка на порожність
    if prices.empty or len(prices['close']) < 2:
        raise ValueError(f"Недостатньо даних для символу {symbol}")

    return prices['close'].iloc[-1] - prices['close'].iloc[0]

# Функція для отримання даних
def get_data(symbol, timeframe='15m', limit=60):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        return pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    except Exception as e:
        logging.error(f"Помилка отримання даних для {symbol}: {str(e)}")
        return pd.DataFrame()


# Розрахунок RSI
def calculate_rsi(prices, period=14):
    delta = pd.Series(prices).diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


# Розрахунок EMA
def calculate_ema(prices, period=50):
    return pd.Series(prices).ewm(span=period).mean().iloc[-1]


# Розрахунок ATR
def calculate_atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr.iloc[-1]


# Розрахунок Bollinger Bands
def calculate_bollinger_bands(prices, period=20):
    sma = pd.Series(prices).rolling(window=period).mean()
    std = pd.Series(prices).rolling(window=period).std()
    return sma + 2 * std, sma - 2 * std


# Розрахунок MACD
def calculate_macd(prices):
    short_ema = calculate_ema(prices, period=12)
    long_ema = calculate_ema(prices, period=26)
    macd = short_ema - long_ema
    signal_line = pd.Series(prices).ewm(span=9).mean().iloc[-1]
    return macd, signal_line


# Розрахунок ADX
def calculate_adx(df, period=14):
    df['tr'] = pd.concat(
        [df['high'] - df['low'], abs(df['high'] - df['close'].shift()), abs(df['low'] - df['close'].shift())],
        axis=1).max(axis=1)
    df['dm_plus'] = (df['high'] - df['high'].shift()).where(
        (df['high'] - df['high'].shift()) > (df['low'].shift() - df['low']), 0)
    df['dm_minus'] = (df['low'].shift() - df['low']).where(
        (df['low'].shift() - df['low']) > (df['high'] - df['high'].shift()), 0)
    df['atr'] = df['tr'].rolling(window=period).mean()
    df['di_plus'] = 100 * (df['dm_plus'].rolling(window=period).mean() / df['atr'])
    df['di_minus'] = 100 * (df['dm_minus'].rolling(window=period).mean() / df['atr'])
    df['dx'] = 100 * abs(df['di_plus'] - df['di_minus']) / (df['di_plus'] + df['di_minus'])
    adx = df['dx'].rolling(window=period).mean().iloc[-1]
    return adx


# Розрахунок Stochastic Oscillator
def calculate_stochastic_oscillator(df, period=14):
    high_max = df['high'].rolling(window=period).max()
    low_min = df['low'].rolling(window=period).min()
    stoch = 100 * (df['close'] - low_min) / (high_max - low_min)
    return stoch.iloc[-1]


# Розрахунок CCI (Commodity Channel Index)
def calculate_cci(df, period=20):
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    sma = typical_price.rolling(window=period).mean()
    mad = typical_price.rolling(window=period).apply(lambda x: np.fabs(x - x.mean()).mean())
    cci = (typical_price - sma) / (0.015 * mad)
    return cci.iloc[-1]


# Розрахунок Parabolic SAR
def calculate_parabolic_sar(df, af=0.02, max_af=0.2):
    sar = df['close'].iloc[0]  # Стартова ціна
    up = df['high'].iloc[0]  # Найвища ціна
    low = df['low'].iloc[0]  # Найнижча ціна
    trend = 1  # Початковий тренд
    af_value = af  # Початковий коефіцієнт прискорення
    for i in range(1, len(df)):
        sar = sar + af_value * (up - sar) if trend == 1 else sar - af_value * (sar - low)
        if trend == 1 and df['low'].iloc[i] < sar:
            trend = -1
            low = df['low'].iloc[i]
            af_value = af
        elif trend == -1 and df['high'].iloc[i] > sar:
            trend = 1
            up = df['high'].iloc[i]
            af_value = af
        if trend == 1 and df['high'].iloc[i] > up:
            up = df['high'].iloc[i]
        elif trend == -1 and df['low'].iloc[i] < low:
            low = df['low'].iloc[i]
    return sar


# Розрахунок часу досягнення цілей
def estimate_time_to_target(current_price, target_price, avg_price_change):
    if avg_price_change == 0:
        return "Невідомо"
    time_to_target = abs((target_price - current_price) / avg_price_change) * 15
    time_delta = timedelta(minutes=time_to_target)
    return (datetime.now() + time_delta).strftime('%H:%M')

# Функція для перевірки коректності розрахунків
def validate_calculations(symbol):
    try:
        # Отримання даних
        df_15m = get_data(symbol, '15m')
        df_1d = get_data(symbol, '1d')

        if df_15m.empty or df_1d.empty:
            return f"Помилка: Пусті дані для {symbol}."

        close_prices_15m = df_15m['close']
        close_prices_1d = df_1d['close']

        # Перевірка кожного розрахунку
        try:
            rsi = calculate_rsi(close_prices_15m)
            assert 0 <= rsi <= 100, "RSI вийшов за межі [0, 100]"
        except Exception as e:
            return f"Помилка в розрахунку RSI для {symbol}: {str(e)}"

        try:
            atr = calculate_atr(df_15m)
            assert atr > 0, "ATR має бути більше 0"
        except Exception as e:
            return f"Помилка в розрахунку ATR для {symbol}: {str(e)}"

        try:
            ema_15m = calculate_ema(close_prices_15m)
            ema_1d = calculate_ema(close_prices_1d)
            assert ema_15m > 0 and ema_1d > 0, "EMA має бути більше 0"
        except Exception as e:
            return f"Помилка в розрахунку EMA для {symbol}: {str(e)}"

        try:
            macd, signal_line = calculate_macd(close_prices_15m)
            assert macd is not None and signal_line is not None, "MACD або Signal Line некоректні"
        except Exception as e:
            return f"Помилка в розрахунку MACD для {symbol}: {str(e)}"

        try:
            adx = calculate_adx(df_15m)
            assert 0 <= adx <= 100, "ADX має бути у діапазоні [0, 100]"
        except Exception as e:
            return f"Помилка в розрахунку ADX для {symbol}: {str(e)}"

        try:
            stoch = calculate_stochastic_oscillator(df_15m)
            assert 0 <= stoch <= 100, "Stochastic має бути у діапазоні [0, 100]"
        except Exception as e:
            return f"Помилка в розрахунку Stochastic для {symbol}: {str(e)}"

        try:
            cci = calculate_cci(df_15m)
            assert -300 <= cci <= 300, "CCI має бути у розумному діапазоні (-300, 300)"
        except Exception as e:
            return f"Помилка в розрахунку CCI для {symbol}: {str(e)}"

        try:
            sar = calculate_parabolic_sar(df_15m)
            assert sar > 0, "SAR має бути більше 0"
        except Exception as e:
            return f"Помилка в розрахунку SAR для {symbol}: {str(e)}"

        # Якщо всі перевірки успішні
        return f"Усі розрахунки для {symbol} виконані успішно!"
    except Exception as e:
        return f"Помилка у функції перевірки для {symbol}: {str(e)}"

# Основна стратегія
def trade_with_targets(symbol, leverage=20, atr_multiplier=1.5):
    df_15m = get_data(symbol, '15m')
    df_1d = get_data(symbol, '1d')

    if df_15m.empty or df_1d.empty:
        return

    close_prices_15m = df_15m['close']
    close_prices_1d = df_1d['close']



    rsi = calculate_rsi(close_prices_15m)
    if rsi > 30 and rsi < 70:
        logging.info(
            f"Сигналів для {symbol} не знайдено. RSI {rsi}")
        return
    atr = calculate_atr(df_15m)
    ema_15m = calculate_ema(close_prices_15m)  # EMA для 15 хвилин
    ema_1d = calculate_ema(close_prices_1d)
    macd, signal_line = calculate_macd(close_prices_15m)
    adx = calculate_adx(df_15m)
    stoch = calculate_stochastic_oscillator(df_15m)
    cci = calculate_cci(df_15m)
    sar = calculate_parabolic_sar(df_15m)  # SAR індикатор
    # Визначення тренду на основі EMA на 1 день
    if ema_1d < close_prices_15m.iloc[-1]:
        trend = "bullish"
    else:
        trend = "bearish"
    low_volatility = atr * 0.8  # Наприклад, низька волатильність
    high_volatility = atr * 1.2  # Висока волатильність

    # Визначення сили тренду
    strong_trend = adx > 25  # Сильний тренд

    # Налаштування коефіцієнтів залежно від ADX і ATR
    if atr < low_volatility and not strong_trend:
        multipliers = [1, 1.3, 1.7]  # Слабкий тренд + низька волатильність (агресивні цілі)
    elif atr > high_volatility and strong_trend:
        multipliers = [0.8, 1, 1.2]  # Сильний тренд + висока волатильність (консервативні цілі)
    elif atr < low_volatility and strong_trend:
        multipliers = [1, 1.3, 1.7]  # Сильний тренд + низька волатильність
    else:
        multipliers = [0.4, 0.6, 0.8]  # Стандартний варіант
    result = analyze_news_impact(symbol)

    # Визначення сигналів для покупки або продажу
    if (trend == "bullish" and rsi < 30 and macd > signal_line and adx > 18 and stoch < 22 and cci < -90 and
            close_prices_15m.iloc[-1] > ema_15m * 1 and close_prices_15m.iloc[-1] > sar * 1 and (
                    result is None or result)):
        direction = "LONG/BUY⬆️"
        stop_loss = close_prices_15m.iloc[-1] - atr * atr_multiplier
        targets = [close_prices_15m.iloc[-1] + atr * atr_multiplier * i for i in multipliers]
    elif (trend == "bearish" and rsi > 70 and macd < signal_line  and adx > 18 and stoch > 78 and cci > 90 and
          close_prices_15m.iloc[-1] < ema_15m * 1 and close_prices_15m.iloc[-1] < sar * 1 and (
                  result is None or not result)):
        direction = "SHORT/SELL⬇️"
        stop_loss = close_prices_15m.iloc[-1] + atr * atr_multiplier
        targets = [close_prices_15m.iloc[-1] - atr * atr_multiplier * i for i in multipliers]

    else:
        if rsi < 30:
            logging.info(f"Сигналів для {symbol} не знайдено. RSI {rsi}   {rsi < 30} {macd > signal_line} {adx>20} {stoch<20} {cci < -100} {(close_prices_15m.iloc[-1] > ema_15m or close_prices_15m.iloc[-1] > sar)} {result}")
            logging.info(f"{close_prices_15m.iloc[-1] > ema_15m} {close_prices_15m.iloc[-1] > sar} {(result is None or result)}")

        else:
            logging.info(f"Сигналів для {symbol} не знайдено. RSI {rsi}   {rsi > 70} {macd < signal_line} {adx>20} {stoch> 80} {cci > 100} {(close_prices_15m.iloc[-1] < ema_15m or close_prices_15m.iloc[-1] < sar)} {result}")
            logging.info(f"{close_prices_15m.iloc[-1] < ema_15m} {close_prices_15m.iloc[-1] < sar} {(result is None or not result)}")
        return
    if rsi < 30:
        logging.info(
            f"Сигналів для {symbol} знайдено. RSI {rsi}   {rsi < 30} {macd > signal_line} {adx > 20} {stoch < 20} {cci < -100} {(close_prices_15m.iloc[-1] > ema_15m or close_prices_15m.iloc[-1] > sar)} {result}")
        logging.info(
            f"{close_prices_15m.iloc[-1] > ema_15m} {close_prices_15m.iloc[-1] > sar} {(result is None or result)}")

    else:
        logging.info(
            f"Сигналів для {symbol} знайдено. RSI {rsi}   {rsi > 70} {macd < signal_line} {adx > 20} {stoch > 80} {cci > 100} {(close_prices_15m.iloc[-1] < ema_15m or close_prices_15m.iloc[-1] < sar)} {result}")
        logging.info(
            f"{close_prices_15m.iloc[-1] < ema_15m} {close_prices_15m.iloc[-1] < sar} {(result is None or not result)}")

    start_message = bot.send_message(
        TELEGRAM_CHAT_ID,
        text=(f"ВНИМАНИЕ СТАРТ СДЕЛКИ\n"
              f"Заходи!!!\n\n"
              f"{symbol} {direction}\n"
              f"Плечи: x{leverage}\n"
              f"РМ: 5.0%\n"
              f"Цена входа {close_prices_15m.iloc[-1]}\n"
              f"SL: {stop_loss}"
              f"Цель 1: {targets[0]} \n"
              f"Цель 2: {targets[1]} \n "
              f"Цель 3: {targets[2]} \n")
    )
    start_message_id = start_message.message_id  # Зберігаємо ID вихідного повідомлення

    # Цикл перевірки досягнення цілей і стоп-лосса
    while targets:
        price = get_data(symbol)['close'].iloc[-1]

        if direction.startswith("LONG") and price >= targets[0]:
            if len(targets) >= 3:
                bot.send_message(
                    TELEGRAM_CHAT_ID,
                    text=f"Ціль {targets.pop(0)} досягнута!\nСтоп лосс поставил к TBX",
                    reply_to_message_id=start_message_id  # Відповідь на початкове повідомлення
                )
            bot.send_message(
                TELEGRAM_CHAT_ID,
                text=f"Ціль {targets.pop(0)} досягнута!",
                reply_to_message_id=start_message_id  # Відповідь на початкове повідомлення
            )
        elif direction.startswith("SHORT") and price <= targets[0]:
            if len(targets) >= 3:
                bot.send_message(
                    TELEGRAM_CHAT_ID,
                    text=f"Ціль {targets.pop(0)} досягнута!\nСтоп лосс поставил к TBX",
                    reply_to_message_id=start_message_id  # Відповідь на початкове повідомлення
                )
            bot.send_message(
                TELEGRAM_CHAT_ID,
                text=f"Ціль {targets.pop(0)} досягнута!",
                reply_to_message_id=start_message_id  # Відповідь на початкове повідомлення
            )
        elif price <= stop_loss and direction.startswith("LONG") or price >= stop_loss and direction.startswith(
                "SHORT"):
            bot.send_message(
                TELEGRAM_CHAT_ID,
                text="Стоп-лосс досягнуто!",
                reply_to_message_id=start_message_id
            )
            break

        tm.sleep(10)

# Основний цикл
while True:
    for symbol in [
    'DOGE/USDT', 'SHIB/USDT', 'SOL/USDT', 'LTC/USDT', 'XRP/USDT',
    'ADA/USDT', 'AVAX/USDT', 'DOT/USDT', 'LUNA/USDT', 'VET/USDT',
    'FIL/USDT', 'TRX/USDT', 'LINK/USDT', 'BNB/USDT', 'ATOM/USDT',
    'UNI/USDT', 'AAVE/USDT', 'ALGO/USDT', 'FTT/USDT', 'BTC/USDT',
    'ETH/USDT', 'MKR/USDT', 'SUSHI/USDT', 'TWT/USDT', 'BCH/USDT',
    'STMX/USDT', 'GRT/USDT', 'STPT/USDT', 'VTHO/USDT', 'MITH/USDT',
    'NKN/USDT', 'KSM/USDT', 'KAVA/USDT', 'LEND/USDT', 'MANA/USDT',
    'ZRX/USDT', 'XLM/USDT', 'SAND/USDT', 'MATIC/USDT',
    'GALA/USDT', 'FET/USDT', 'IOST/USDT', 'KNC/USDT', 'BNT/USDT',
    'CTSI/USDT', 'KDA/USDT', 'RUNE/USDT', 'FLOW/USDT', 'SUSHI/USDT',
    'PERL/USDT', 'STPT/USDT', 'GMT/USDT', 'NEAR/USDT',
    'LEND/USDT', 'KSM/USDT', 'MITH/USDT', 'VTHO/USDT', 'FET/USDT',
    'HNT/USDT', 'FLOKI/USDT', 'DGB/USDT', 'SAND/USDT', 'XNO/USDT',
    'QTUM/USDT', 'YFI/USDT', 'ICP/USDT', 'PAXG/USDT',
    'STMX/USDT', 'REEF/USDT', 'SNT/USDT', 'YGG/USDT',
    'STPT/USDT', 'ZRX/USDT', 'XEM/USDT', 'BAND/USDT', 'PERL/USDT',
    'DOCK/USDT', 'MDX/USDT', 'VET/USDT', 'TWT/USDT',
    'AAVE/USDT', 'MKR/USDT', 'CVC/USDT', 'TRB/USDT', 'SKL/USDT',
    'EGLD/USDT', 'TWT/USDT', 'SHIB/USDT', 'COTI/USDT', 'FIL/USDT', 'AAVE/USDT',
    'YFI/USDT', 'ZRX/USDT', 'SKL/USDT', 'CHZ/USDT', 'BAND/USDT'
]:
        trade_with_targets(symbol)

        # Затримка між циклами для уникнення перевантаження API
    tm.sleep(2)
    for symbol in [
        "CAKE/USDT", "BAL/USDT", "COMP/USDT", "ZEN/USDT", "BAT/USDT",
        "REN/USDT", "OCEAN/USDT", "WOO/USDT", "ALICE/USDT", "SLP/USDT",
        "LPT/USDT", "DODO/USDT", "BEL/USDT", "CTK/USDT", "FIO/USDT",
        "BETA/USDT", "LDO/USDT", "CFX/USDT", "MINA/USDT", "IMX/USDT",
        "ENS/USDT", "ALPHA/USDT", "TLM/USDT", "MASK/USDT", "LOKA/USDT",
        "POND/USDT", "LTO/USDT", "NMR/USDT", "ONG/USDT", "ONT/USDT",
        "HOT/USDT", "RVN/USDT", "REQ/USDT", "QNT/USDT", "JST/USDT",
        "HBAR/USDT", "ICX/USDT", "ROSE/USDT", "KLAY/USDT", "APE/USDT", "GLMR/USDT", "FTM/USDT", "SNX/USDT",
        "ZIL/USDT", "CHR/USDT", "PHA/USDT", "PROM/USDT", "SC/USDT",
        "DENT/USDT", "PERP/USDT", "ARPA/USDT", "LINA/USDT", "BAKE/USDT",
        "SXP/USDT", "XTZ/USDT", "AXS/USDT", "ENJ/USDT", "ILV/USDT",
        "OXT/USDT", "CKB/USDT", "MTL/USDT", "FIRO/USDT", "STG/USDT",
        "BLZ/USDT", "CELR/USDT"
    ]:
        trade_with_targets(symbol)

        # Затримка між циклами для уникнення перевантаження API
    tm.sleep(2)
    for symbol in [
        "ACH/USDT", "AGIX/USDT", "AMP/USDT", "ANKR/USDT", "API3/USDT",
        "AR/USDT", "ATA/USDT", "AUCTION/USDT", "AVA/USDT",
         "BAR/USDT", "BICO/USDT", "BNX/USDT",
        "BTS/USDT", "BTTC/USDT", "C98/USDT",
        "CITY/USDT", "CREAM/USDT","DAR/USDT",
        "DATA/USDT", "DEGO/USDT", "DF/USDT", "DNT/USDT",
        "DYDX/USDT", "ELF/USDT", "ERN/USDT",
        "FARM/USDT", "FOR/USDT", "FORTH/USDT", "GAS/USDT", "GMX/USDT",
        "GNO/USDT", "GTC/USDT", "HIGH/USDT", "HIVE/USDT", "IDEX/USDT",
        "INJ/USDT", "IQ/USDT", "JASMY/USDT", "JOE/USDT", "KMD/USDT",
        "KP3R/USDT", "LAZIO/USDT", "LEVER/USDT", "LIT/USDT",
        "LRC/USDT", "MBOX/USDT", "MC/USDT", "MDT/USDT", "MOVR/USDT",
        "OG/USDT", "OGN/USDT", "OOKI/USDT", "OP/USDT",
        "PEOPLE/USDT", "POWR/USDT", "PUNDIX/USDT", "PYR/USDT", "QKC/USDT",
        "RAD/USDT", "RAMP/USDT", "RGT/USDT", "RNDR/USDT",
        "RSR/USDT", "SPELL/USDT", "SRM/USDT",
        "SUN/USDT", "SUPER/USDT", "SYN/USDT", "T/USDT", "TRIBE/USDT",
         "UNFI/USDT", "UTK/USDT", "WIN/USDT",
        "XEC/USDT", "XVG/USDT"
    ]:
        trade_with_targets(symbol)

        # Затримка між циклами для уникнення перевантаження API
    tm.sleep(2)