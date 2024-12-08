import telebot
import time
import googleapiclient.discovery
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
import requests
import os
import random  # Для генерації випадкових текстів
import sqlite3 as sq
from config import Bot_token, admin_id, Text  # Импорт API ключей из config.py

bot = telebot.TeleBot(Bot_token)

markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
New_search = telebot.types.KeyboardButton('Нова підбірка каналів')
New_chanel = telebot.types.KeyboardButton('Новий канал')
Ref_chanel = telebot.types.KeyboardButton('Реферальна програма')
info_chanel = telebot.types.KeyboardButton('Інформація')
markup.add(New_search, New_chanel, Ref_chanel, info_chanel)

def create_markup_referal():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton('Створити реферальний код'))
    markup.add(telebot.types.KeyboardButton('Ввести реферальний код'))
    markup.add(telebot.types.KeyboardButton('Назад'))
    return markup

def create_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton('Оновити API ключ'))
    markup.add(telebot.types.KeyboardButton('Оновити пошукове слово'))
    markup.add(telebot.types.KeyboardButton('Запустити пошук'))
    markup.add(telebot.types.KeyboardButton('Переглянути дані'))
    markup.add(telebot.types.KeyboardButton('Назад'))
    return markup
markup_stop = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
markup_stop_button = telebot.types.KeyboardButton('    ')
markup_stop.add(markup_stop_button)

markup_info = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
API_info = telebot.types.KeyboardButton('Що таке Api-key?')
Frige_info = telebot.types.KeyboardButton('Хто такий фрідж?')
rek_info = telebot.types.KeyboardButton('Реклама')
back = telebot.types.KeyboardButton('Назад')
markup_info.add(API_info, Frige_info, rek_info, back)
# Список шаблонів повідомлень
channel_messages = [
    '''
Привет!
Я заметил твой YouTube-канал "{channel_name}", и он, кажется, давно не обновлялся. Возможно, это то, что тебе интересно обсудить.
Я готов предложить отличные условия для его приобретения. Если это тебя заинтересует, напиши!
''',
    '''
Здравствуйте!
Я нашел ваш YouTube-канал "{channel_name}", и мне показалось, что он уже давно неактивен. Есть идея, как его можно возродить.
Если это для вас актуально, я готов сделать привлекательное предложение!
''',
    '''
Привет!
Твой канал "{channel_name}" привлек мое внимание, хотя кажется, что он давно не обновлялся. У меня есть предложение, которое может быть тебе интересно.
Если тебе это подходит, свяжись со мной, и обсудим!
''',
    '''
Здравствуйте!
Ваш канал "{channel_name}" давно не обновлялся. Я заинтересован в его приобретении.
Если готовы обсудить детали, напишите мне. Это может быть выгодно для нас обоих!
''',
    '''
Привет!
Наткнулся на твой канал "{channel_name}". Похоже, что он в состоянии покоя.
У меня есть идея по его восстановлению и готов предложить хорошую цену. Напиши, если заинтересован!

Привет!
Я увидел твой канал "{channel_name}", и кажется, что он не обновляется уже какое-то время. У меня есть предложение по его восстановлению, если тебе это интересно.
Давай обсудим, что можно сделать!
''',
    '''
Здравствуйте!
Ваш канал "{channel_name}" давно неактивен, и это привлекло мое внимание. Я готов предложить выгодные условия для его покупки и восстановления.
Если вам это интересно, свяжитесь со мной!
''',
    '''
Привет!
Ты владеешь каналом "{channel_name}", и, похоже, он давно не обновлялся. У меня есть несколько идей по его возвращению в активную фазу.
Если ты открыт для предложения, напиши мне!
''',
    '''
Здравствуйте!
Ваш канал "{channel_name}" давно не обновлялся. Я хотел бы предложить вам выгодное предложение по его приобретению и восстановлению.
Если это вас интересует, напишите мне!
''',
    '''
Привет!
Твой канал "{channel_name}" давно не обновляется, и я вижу в этом шанс для обоих. Я готов предложить достойные условия для его приобретения.
Если тебе интересно, напиши мне!
''',
'''
Привет!
Обратил внимание, что твой канал "{channel_name}" давно не обновляется. У меня есть интересное предложение по его покупке. Если тебе это актуально, напиши мне, обсудим!
''',
'''
Привет!
Я заметил, что канал "{channel_name}" больше не ведется. Хотел бы обсудить возможность его приобретения на взаимовыгодных условиях. Жду твоего ответа!
''',
'''
Добрый день!
Канал "{channel_name}" выглядит перспективным, но вижу, что он не обновляется. Готов обсудить его покупку. Если тебе интересно, напиши мне!
''',
'''
Приветствую!
Обратил внимание, что канал "{channel_name}" давно не активен. У меня есть идея, как его использовать, и желание его приобрести. Давай обсудим?
''',
'''
Привет!
Твой канал "{channel_name}" заинтересовал меня. Похоже, он сейчас простаивает, и я готов предложить за него хорошую сумму. Что скажешь?
''',
'''
Добрый день!
Я обратил внимание на канал "{channel_name}" и вижу, что он неактивен. Хочу предложить сделку — если тебе интересно, напиши!
''',
'''
Привет!
Канал "{channel_name}" выглядит круто, но вижу, что обновлений давно не было. У меня есть интерес к его покупке. Жду твоего ответа!
''',
'''
Приветствую!
Канал "{channel_name}" давно не ведется, а я готов предложить достойные условия для его приобретения. Если идея интересна, напиши мне!
''',
'''
Привет!
Обратил внимание, что канал "{channel_name}" не обновляется. Если ты думаешь о его продаже, я готов обсудить детали. Напиши мне!
''',
'''
Добрый день!
Канал "{channel_name}" интересует меня как проект. Вижу, что он давно не обновлялся, и готов предложить за него хорошую цену. Напиши, если это актуально!
'''
]


# Пропускаємо старі оновлення
def skip_old_updates():
    updates = bot.get_updates(timeout=1)
    if updates:
        # Беремо ID останнього оновлення
        return updates[-1].update_id + 1
    return None

# Отримуємо останній update_id
last_update_id = skip_old_updates()

channel_message = ''
start_ros = 0
# Функція для отримання повідомлення від адміністратора
def get_message_from_admin(message):
    global channel_message
    global start_ros
    start_ros = 0
    # Запит у адміністратора тексту
    channel_message = ''
    bot.send_message(message.from_user.id, "Введіть текст повідомлення, яке потрібно надіслати всім користувачам", reply_markup=markup_stop)
    start_ros = 1

# Використання функції в розсилці
def get_random_channel_message():
    global channel_message
    # Запитуємо у адміністратора повідомлення
    message = channel_message
    return message
def get_random_message(channel_name):
    return random.choice(channel_messages).format(channel_name=channel_name)

# Функція для надсилання повідомлень усім користувачам
def send_messages_to_users(message):
    with sq.connect("Chanels_base.db") as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM users")
        users = cur.fetchall()
        if channel_message != '':
            for user in users:
                user_id = user[0]
                try:
                    bot.send_message(user_id, get_random_channel_message())
                except Exception as e:
                    bot.send_message(admin_id, f"Помилка відправки користувачу {user_id}: {e}")
        else:
            get_message_from_admin(message)

# Подключение к базе данных и создание таблицы, если она не существует
with sq.connect("User_chanel.db") as con:
    cur = con.cursor()
    # Створюємо таблицю для користувачів
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_chanel (
            user_id INTEGER,
            name_chanel TEXT,
            id_chanel TEXT
        )
    """)
with sq.connect("User_referal.db") as con:
    cur = con.cursor()
    # Створюємо таблицю для користувачів
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_referal (
            user_id INTEGER,
            name_referal INTEGER DEFAULT 0,
            add_num INTEGER DEFAULT 0,
            join_referal INTEGER DEFAULT 0
        )
    """)
with sq.connect("User_data.db") as con:
    cur = con.cursor()
    # Створюємо таблицю для користувачів
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id INTEGER PRIMARY KEY,
            api_key TEXT,
            keyword TEXT, 
            num_buy INTEGER DEFAULT 0
        )
    """)
with sq.connect("Chanels_base.db") as con:
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT,
            num_newchanel INTEGER DEFAULT 0,
            num_buy INTEGER DEFAULT 0,
            searchchannels INTEGER DEFAULT 0,
            run INTEGER DEFAULT 0
        )
    """)
# Функція для збереження даних користувача в базі
def save_user_data(user_id, api_key=None, keyword=None):
    with sq.connect("User_data.db") as con:
        cur = con.cursor()

        # Перевіряємо, чи є дані для цього користувача
        cur.execute("SELECT * FROM user_data WHERE user_id = ?", (user_id,))
        user_data = cur.fetchone()

        if user_data:
            # Якщо користувач вже є, оновлюємо його дані
            if api_key:
                cur.execute("UPDATE user_data SET api_key = ? WHERE user_id = ?", (api_key, user_id))
            if keyword:
                cur.execute("UPDATE user_data SET keyword = ? WHERE user_id = ?", (keyword, user_id))
        else:
            # Якщо користувача немає, додаємо новий запис
            cur.execute("INSERT INTO user_data (user_id, api_key, keyword) VALUES (?, ?, ?)",
                        (user_id, api_key, keyword))

        con.commit()


# Функція для пошуку каналів (це ваша функція, замініть її на свою реалізацію)
def main_search(user_id):
    with sq.connect("User_data.db") as con:
        cur = con.cursor()
        cur.execute("SELECT api_key, keyword FROM user_data WHERE user_id = ?", (user_id,))
        api_key, keyword = cur.fetchone()

    # Логіка пошуку каналів (приклад, ваш код тут)
    bot.send_message(user_id, f"Пошук каналів за ключовим словом '{keyword}' із API ключем {api_key}...")
    # Тут можна реалізувати пошук каналів на YouTube або іншому сервісі


# Функция для добавления пользователя в базу данных, если его еще нет
def add_user_to_db(user_id, username, mes):
    with sq.connect("Chanels_base.db") as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if cur.fetchone() is None:  # Если пользователя нет в базе
            cur.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
            print(f"Пользователь добавлен в базу данных: {user_id} с username {username}")
            bot.send_message(mes, 'Привіт 🌝🤚.', reply_markup=markup)
        else:
            bot.send_message(mes, 'Ми з тобою вже знайомі!', reply_markup=markup)
def add_user_to_db_ref(user_id, mes):
    with sq.connect("User_referal.db") as con:
        cur = con.cursor()
        cur.execute("SELECT user_id FROM user_referal WHERE user_id = ?", (user_id,))
        if cur.fetchone() is None:  # Если пользователя нет в базе
            a = []
            b = ''
            for i in range(9):
                a.append(random.randint(1, 100))
            for c in a:
                b = b.join(str(c))
            cur.execute("INSERT INTO user_referal (user_id, name_referal) VALUES (?, ?)", (int(user_id), b))


# Функция для проверки регистрации пользователя
def is_user_registered(user_id):
    with sq.connect("Chanels_base.db") as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        return cur.fetchone() is not None  # Возвращает True, если пользователь существует

@bot.message_handler(commands=['start'])
def Start(message):
    add_user_to_db(message.from_user.id, message.from_user.username, message.chat.id)  # Записуємо username
    bot.send_message(message.from_user.id, "Удачних пошуків сищик)", reply_markup=markup)

@bot.message_handler(commands=['start-sms'])
def Start_sms(message):
    global channel_message
    if message.from_user.username == 'vladuslavmen':
        send_messages_to_users(message)
        channel_message = ''
# Обробка натискання кнопки "Нова підбірка каналів"
@bot.message_handler(func=lambda message: message.text == 'Нова підбірка каналів')
def handle_new_collection(message):
    user_id = message.from_user.id
    # Перевіряємо, чи є користувач в базі
    with sq.connect("User_data.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM user_data WHERE user_id = ?", (user_id,))
        user_data = cur.fetchone()

    if user_data:
        bot.send_message(user_id, "Оберіть дію:", reply_markup=create_markup())
    else:
        # Якщо користувача немає в базі, створюємо новий запис
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO user_data (user_id, api_key, keyword, num_buy) VALUES (?, ?, ?, ?)", (user_id, '', '', 1))
            con.commit()
        bot.send_message(user_id, "Оберіть дію:", reply_markup=create_markup())

# Обробка натискання кнопки "Оновити API ключ"
@bot.message_handler(func=lambda message: message.text == 'Оновити API ключ')
def update_api_key(message):
    user_id = message.from_user.id

    # Перевіряємо, чи є користувач в базі
    with sq.connect("User_data.db") as con:
        cur = con.cursor()
        cur.execute("SELECT api_key FROM user_data WHERE user_id = ?", (user_id,))
        api_key = cur.fetchone()

    if api_key:
        bot.send_message(user_id, "Введіть новий API ключ:")
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (user_id,))
            cur.execute("""
                                                            UPDATE user_data
                                                            SET num_buy = 2
                                                            WHERE user_id = ?
                                                        """, (message.from_user.id,))
            con.commit()
    else:
        bot.send_message(user_id, "API ключ не знайдений. Створюємо новий запис.")
        # Якщо API ключ не знайдений, запитуємо його
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO user_data (user_id, api_key, keyword) VALUES (?, ?, ?)", (user_id, '', ''))
            con.commit()

        bot.send_message(user_id, "Введіть новий API ключ:")
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (user_id,))
            cur.execute("""
                                                            UPDATE user_data
                                                            SET num_buy = 2
                                                            WHERE user_id = ?
                                                        """, (message.from_user.id,))
            con.commit()

# Обробка натискання кнопки "Оновити пошукове слово"
@bot.message_handler(func=lambda message: message.text == 'Оновити пошукове слово')
def update_keyword(message):
    user_id = message.from_user.id

    # Перевіряємо, чи є користувач в базі
    with sq.connect("User_data.db") as con:
        cur = con.cursor()
        cur.execute("SELECT keyword FROM user_data WHERE user_id = ?", (user_id,))
        keyword = cur.fetchone()

    if keyword:
        bot.send_message(user_id, "Введіть нове ключове слово для пошуку каналів:")
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (user_id,))
            cur.execute("""
                                                            UPDATE user_data
                                                            SET num_buy = 3
                                                            WHERE user_id = ?
                                                        """, (message.from_user.id,))
            con.commit()
    else:
        bot.send_message(user_id, "Пошукове слово не знайдено. Створюємо новий запис.")
         # Якщо пошукове слово не знайдено, запитуємо його
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO user_data (user_id, api_key, keyword) VALUES (?, ?, ?)", (user_id, '', ''))
            con.commit()
        bot.send_message(user_id, "Введіть нове ключове слово для пошуку каналів:")
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (user_id,))
            cur.execute("""
                                                            UPDATE user_data
                                                            SET num_buy = 3
                                                            WHERE user_id = ?
                                                        """, (message.from_user.id,))
            con.commit()

# Обробка натискання кнопки "Запустити пошук"
@bot.message_handler(func=lambda message: message.text == 'Запустити пошук')
def start_search(message):
    user_id = message.from_user.id

    # Перевіряємо, чи є дані для користувача
    with sq.connect("User_data.db") as con:
        cur = con.cursor()
        cur.execute("SELECT api_key, keyword FROM user_data WHERE user_id = ?", (user_id,))
        user_data = cur.fetchone()

    if user_data:
        api_key, keyword = user_data
        if api_key and keyword:
            bot.send_message(user_id,
                                f"Пошук за ключовим словом '{keyword}' із API ключем {api_key} розпочинається...")
            # Викликаємо функцію для пошуку каналів
            main_search(api_key, keyword, message)
        else:
            bot.send_message(user_id, "Необхідно ввести API ключ та ключове слово перед запуском пошуку.")
    else:
        bot.send_message(user_id,
                            "Ви ще не ввели API ключ або пошукове слово. Будь ласка, спочатку налаштуйте ці дані.")
start = 0
keyword = ''
api_key = ''
@bot.message_handler(content_types=['text'])
def main(message):
    global start
    global keyword
    global api_key
    global start_ros
    global channel_message
    time.sleep(1)  # Затримка в 1 секунду

    if not is_user_registered(message.from_user.id):
        bot.send_message(message.chat.id, "Ви не зареєстровані! Будь ласка, введіть команду /start для реєстрації.")
        return

    with sq.connect("Chanels_base.db") as con:
        cur = con.cursor()
        # Отримуємо значення num_buy для користувача
        cur.execute("SELECT num_buy FROM users WHERE id = ?", (message.from_user.id,))
        num_buy = cur.fetchone()[0]

    if num_buy == 0:
        if start_ros == 1:
            channel_message = message.text
            bot.send_message(message.from_user.id, f"Текст для реклами збережено:\n\n{channel_message}", reply_markup=markup)
            start_ros = 0
            send_messages_to_users(message)
        if message.text == 'Реферальна програма':
            bot.send_message(message.chat.id, '''
Не забувай про реферальну систему нашого бота!
За кожного користувача, якого ти приведеш, ти отримаєш +10 доступних каналів.
                    ''', reply_markup=create_markup_referal())
        elif message.text == 'Переглянути дані':
            with sq.connect("User_data.db") as con:
                cur = con.cursor()
                cur.execute("SELECT api_key, keyword FROM user_data WHERE user_id = ?", (message.chat.id,))
                result = cur.fetchone()
                api_key, keyword = result
                bot.send_message(message.chat.id, f"Ваш апі ключ:\n{api_key}\nВаше пошукове слово:\n{keyword}", reply_markup=markup)
        elif message.text == 'Створити реферальний код':
            with sq.connect("User_referal.db") as con:
                cur = con.cursor()
                cur.execute("SELECT name_referal, add_num, join_referal FROM user_referal WHERE user_id = ?",
                            (message.from_user.id,))
                result = cur.fetchone()
                if result:
                    name_referal, add_num, join_referal = result
                    print(
                        f"Користувач: {message.from_user.id} з username {message.from_user.username} реферальний код {name_referal} кількість приглашоних {add_num}")
                    if join_referal == 0:
                        bot.send_message(message.chat.id, f'Ось ваш реферальний код:')
                        bot.send_message(message.chat.id,
                                         f'{name_referal}')
                        bot.send_message(message.chat.id,
                                         f'Кількість доступних каналів по рефералці: {add_num}. Ви ще не ввели реферальний код друга.')
                    else:
                        bot.send_message(message.chat.id, f'Ось ваш реферальний код:')
                        bot.send_message(message.chat.id,
                                         f'{name_referal}')
                        bot.send_message(message.chat.id,
                                         f'Кількість доступних каналів по рефералці: {add_num}. Реферальний код, за яким ви приєдналися:')
                        bot.send_message(message.chat.id,
                                         f'{join_referal}.', reply_markup=create_markup_referal())
                else:
                    add_user_to_db_ref(message.from_user.id, message)
                    with sq.connect("User_referal.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT name_referal, add_num FROM user_referal WHERE user_id = ?",
                                    (message.from_user.id,))
                        result = cur.fetchone()
                        name_referal, add_num = result
                        bot.send_message(message.chat.id, f'Ось ваш реферальний код:')
                        bot.send_message(message.chat.id,
                                         f'{name_referal}')
                        bot.send_message(message.chat.id,
                                         f'Кількість запрошених користувачів: {add_num}. Ви ще не ввели реферальний код друга.',
                                         reply_markup=create_markup_referal())
        elif message.text == 'Ввести реферальний код':
            with sq.connect("User_referal.db") as con:
                cur = con.cursor()
                cur.execute("SELECT join_referal FROM user_referal WHERE user_id = ?",
                            (message.from_user.id,))
                result = cur.fetchone()
                if result:
                    join_referal = result[0]
                    if join_referal == 0:
                        bot.send_message(message.chat.id,
                                         f'Введіть реферальний код користувача який вас пригласив:',
                                         reply_markup=markup_stop)

                    else:
                        bot.send_message(message.chat.id,
                                         f'Ви вже ввели реферальний код: \n{join_referal}',
                                         reply_markup=markup)
                else:
                    add_user_to_db_ref(message.from_user.id, message)
        elif message.text == 'Новий канал':
            with sq.connect("Chanels_base.db") as con:
                cur = con.cursor()

                # Отримуємо дані користувача
                cur.execute("SELECT num_newchanel FROM users WHERE id = ?", (message.from_user.id,))
                chanel_num = cur.fetchone()[0]
                if chanel_num < 20:
                    with sq.connect("User_chanel.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT name_chanel, id_chanel FROM user_chanel WHERE user_id = ?",
                                    (message.from_user.id,))
                        result = cur.fetchone()

                        if result:  # Якщо є результат
                            print(
                                f"Користувач отримує канал: {message.from_user.id} з username {message.from_user.username}")
                            name_chanel, id_chanel = result
                            channel_id = id_chanel
                            channel_name = name_chanel
                            youtube_link = f'https://www.youtube.com/channel/{channel_id}'

                            # Відправляємо канал користувачу
                            bot.send_message(
                                message.chat.id,
                                f"Канал: {channel_name}\nПосилання: {youtube_link}"
                            )
                            # Відправляємо повідомлення з випадковим текстом
                            bot.send_message(message.chat.id, get_random_message(channel_name), reply_markup=markup)
                        else:
                            bot.send_message(message.chat.id, 'Щасти!', reply_markup=markup_stop)
                            print(f"Користувач отримує канал: {message.from_user.id} з username {message.from_user.username}")
                            process_channels(message, False)  # Викликаємо функцію обробки каналів
                else:
                    with sq.connect("User_chanel.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT name_chanel, id_chanel FROM user_chanel WHERE user_id = ?",
                                    (message.from_user.id,))
                        result = cur.fetchone()

                        if result:  # Якщо є результат
                            print(
                                f"Користувач отримує канал: {message.from_user.id} з username {message.from_user.username}")
                            name_chanel, id_chanel = result
                            channel_id = id_chanel
                            channel_name = name_chanel
                            youtube_link = f'https://www.youtube.com/channel/{channel_id}'

                            # Відправляємо канал користувачу
                            bot.send_message(
                                message.chat.id,
                                f"Канал: {channel_name}\nПосилання: {youtube_link}"
                            )
                            # Відправляємо повідомлення з випадковим текстом
                            cur.execute(
                                "DELETE FROM user_chanel WHERE user_id = ? AND name_chanel = ? AND id_chanel = ?",
                                (message.from_user.id, name_chanel, id_chanel))
                            con.commit()
                            bot.send_message(message.chat.id, get_random_message(channel_name), reply_markup=markup)
                        else:
                            with sq.connect("Chanels_base.db") as con:
                                cur = con.cursor()
                                cur.execute("SELECT searchchannels FROM users WHERE id = ?", (message.from_user.id,))
                                searchchannels = cur.fetchone()[0]
                                if searchchannels < 0:
                                    cur.execute("""
                                                                                                    UPDATE users
                                                                                                    SET searchchannels = 0
                                                                                                    WHERE id = ?
                                                                                                """,
                                                (message.from_user.id,))
                                    con.commit()
                                if searchchannels == 0:
                                    try:
                                        with sq.connect("User_referal.db") as con:
                                            cur = con.cursor()
                                            cur.execute("SELECT add_num FROM user_referal WHERE user_id = ?",
                                                        (message.from_user.id,))
                                            result = cur.fetchone()  # fetchone() может вернуть None
                                            if result[0] > 0:
                                                bot.send_message(message.chat.id, 'Щасти!', reply_markup=markup_stop)
                                                print(
                                                    f"Користувач отримує канал: {message.from_user.id} з username {message.from_user.username}")
                                                process_channels(message, False)  # Викликаємо функцію обробки каналів
                                                cur.execute("""
                                                                                                                UPDATE users
                                                                                                                SET add_num = add_num - 1
                                                                                                                WHERE id = ?
                                                                                                            """,
                                                            (message.from_user.id,))
                                                con.commit()
                                            else:
                                                bot.send_message(message.chat.id, 'Щасти!', reply_markup=markup)
                                                bot.send_message(message.chat.id, 'Упс! Схоже, всі канали вичерпано. Створюй власну підбірку каналів або придбай преміум версію з уже готовою базою даних каналів у @vladuslavmen.')
                                                print(f"Користувач досяг 20 каналів: {message.from_user.id} з username {message.from_user.username}")
                                    except BaseException as e:
                                        add_user_to_db_ref(message.from_user.id, message)
                                        with sq.connect("User_referal.db") as con:
                                            cur = con.cursor()
                                            cur.execute("SELECT add_num FROM user_referal WHERE user_id = ?",
                                                        (message.from_user.id,))
                                            result = cur.fetchone()  # fetchone() может вернуть None
                                            if result[0] > 0:
                                                bot.send_message(message.chat.id, 'Щасти!', reply_markup=markup_stop)
                                                print(
                                                    f"Користувач отримує канал: {message.from_user.id} з username {message.from_user.username}")
                                                process_channels(message, False)  # Викликаємо функцію обробки каналів
                                                cur.execute("""
                                                                                                                UPDATE users
                                                                                                                SET add_num = add_num - 1
                                                                                                                WHERE id = ?
                                                                                                            """,
                                                            (message.from_user.id,))
                                                con.commit()
                                            else:
                                                bot.send_message(message.chat.id, 'Щасти!', reply_markup=markup)
                                                bot.send_message(message.chat.id,
                                                                 'Упс! Схоже, всі канали вичерпано. Створюй власну підбірку каналів або придбай преміум версію з уже готовою базою даних каналів у @vladuslavmen.')
                                                print(
                                                    f"Користувач досяг 20 каналів: {message.from_user.id} з username {message.from_user.username}")
                                else:
                                    with sq.connect("Chanels_base.db") as con:
                                        cur = con.cursor()
                                        bot.send_message(message.chat.id, 'Щасти!', reply_markup=markup_stop)
                                        print(f"Користувач отримує канал: {message.from_user.id} з username {message.from_user.username}")
                                        process_channels(message, False)  # Викликаємо функцію обробки каналів
                                        cur.execute("""
                                                                    UPDATE users
                                                                    SET searchchannels = searchchannels - 1
                                                                    WHERE id = ?
                                                                """, (message.from_user.id,))
                                        con.commit()
        elif message.text == 'Інформація':
            bot.send_message(message.chat.id, f'{Text[3]}', reply_markup=markup_info)
        elif message.text == 'Що таке Api-key?':
            bot.send_message(message.chat.id, f'{Text[0]}', reply_markup=markup)
            video_path = "IMG_7671.MP4"

            try:
                # Відкриваємо відеофайл у двійковому режимі
                with open(video_path, 'rb') as video:
                    bot.send_video(message.chat.id, video, caption="Ось приклад!")
                print(f"Відео успішно надіслано користувачеві {message.chat.id}.")
            except FileNotFoundError:
                bot.send_message(message.chat.id, "Відеофайл не знайдено.")
                print("Помилка: Відеофайл не знайдено.")
            except Exception as e:
                bot.send_message(message.chat.id, "Не вдалося надіслати відео.")
                print(f"Помилка: {e}")
        elif message.text == 'Хто такий фрідж?':
            bot.send_message(message.chat.id, f'{Text[1]}', reply_markup=markup)
        elif message.text == 'Реклама':
            bot.send_message(message.chat.id, f'{Text[2]}', reply_markup=markup)
        elif message.text == 'Назад':
            bot.send_message(message.chat.id, '<--', reply_markup=markup)
        elif message.text == 'Переглянути дані':
            with sq.connect("User_data.db") as con:
                cur = con.cursor()
                cur.execute("SELECT api_key, keyword FROM user_data WHERE user_id = ?", (message.chat.id,))
                result = cur.fetchone()
                api_key, keyword = result
                bot.send_message(message.chat.id, f"Ваш апі ключ:\n{api_key}\nВаше пошукове слово:\n{keyword}", reply_markup=markup)
        else:
            with sq.connect("User_data.db") as con:
                cur = con.cursor()
                cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (message.chat.id,))
                num_buy = cur.fetchone()  # fetchone() может вернуть None
                if num_buy is not None:
                    num_buy = num_buy[0]
            if num_buy == 3:
                keyword = message.text
                bot.send_message(message.from_user.id, f"Пошукове слово збережено:\n\n{keyword}")
                with sq.connect("User_data.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (message.chat.id,))
                    cur.execute("""
                                        UPDATE user_data
                                        SET num_buy = 0, keyword = ?
                                        WHERE user_id = ?
                                    """, (message.text, message.from_user.id))
                    con.commit()
                main_search(api_key, keyword, message)
            elif num_buy == 2:
                api_key = message.text
                bot.send_message(message.from_user.id, f"API ключ збережено:\n\n{api_key}")
                with sq.connect("User_data.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (message.chat.id,))
                    cur.execute("""
                                        UPDATE user_data
                                        SET num_buy = 0, api_key = ?
                                        WHERE user_id = ?
                                    """, (message.text, message.from_user.id))
                    con.commit()
            elif len(message.text) > 8:
                try:
                    key = int(message.text)
                    with sq.connect("User_referal.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT name_referal FROM user_referal;")
                        result = cur.fetchall()
                        with sq.connect("User_referal.db") as con1:
                            cur1 = con1.cursor()
                            cur1.execute("SELECT name_referal FROM user_referal WHERE user_id = ?",
                                         (message.from_user.id,))
                            result1 = cur1.fetchone()
                        for res in result:
                            if res[0] == key:
                                if result1[0] == key:
                                    bot.send_message(message.chat.id,
                                                     f'Ви ввели свій код: \n{key}',
                                                     reply_markup=markup)
                                    return
                                else:
                                    cur.execute("""
                                                                            UPDATE user_referal
                                                                            SET join_referal = ?
                                                                            WHERE user_id = ?
                                                                        """, (key, message.from_user.id))
                                    con.commit()
                                    bot.send_message(message.chat.id,
                                                     f'Ви успішно підключились по коду: \n{key}',
                                                     reply_markup=markup)
                                    with sq.connect("User_referal.db") as con:
                                        cur = con.cursor()
                                        cur.execute("""
                                                                                                            UPDATE user_referal
                                                                                                            SET add_num = add_num + 10
                                                                                                            WHERE name_referal = ?""",
                                                    (key,))
                                        con.commit()
                                    return
                        bot.send_message(message.chat.id,
                                         f'Ви ввели не дійсний код: \n{key}',
                                         reply_markup=markup)
                except Exception as e:
                    bot.send_message(message.chat.id, f'Не зрозуміле повідомлення: {message.text}', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f'Не зрозуміле повідомлення: {message.text}', reply_markup=markup)
        return  # Блокуємо подальші дії

    # Якщо num_buy = 1, перевіряємо текст повідомлення
    if message.text == 'Новий канал':
        with sq.connect("User_chanel.db") as con:
            cur = con.cursor()
            cur.execute("SELECT name_chanel, id_chanel FROM user_chanel WHERE user_id = ?",
                        (message.from_user.id,))
            result = cur.fetchone()

            if result:  # Якщо є результат
                print(
                    f"Користувач отримує канал: {message.from_user.id} з username {message.from_user.username}")
                name_chanel, id_chanel = result
                channel_id = id_chanel
                channel_name = name_chanel
                youtube_link = f'https://www.youtube.com/channel/{channel_id}'

                # Відправляємо канал користувачу
                bot.send_message(
                    message.chat.id,
                    f"Канал: {channel_name}\nПосилання: {youtube_link}"
                )
                # Відправляємо повідомлення з випадковим текстом
                cur.execute("DELETE FROM user_chanel WHERE user_id = ? AND name_chanel = ? AND id_chanel = ?",
                            (message.from_user.id, name_chanel, id_chanel))
                con.commit()
                bot.send_message(message.chat.id, get_random_message(channel_name), reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Щасти!', reply_markup=markup_stop)
                print(f"Користувач отримує канал: {message.from_user.id} з username {message.from_user.username}")
                process_channels(message, True)  # Викликаємо функцію обробки каналів
    elif message.text == 'Переглянути дані':
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("SELECT api_key, keyword FROM user_data WHERE user_id = ?", (message.chat.id,))
            result = cur.fetchone()
            api_key, keyword = result
            bot.send_message(message.chat.id, f"Ваш апі ключ:\n{api_key}\nВаше пошукове слово:\n{keyword}",
                             reply_markup=markup)
    elif start_ros == 1:
        channel_message = message.text
        bot.send_message(message.from_user.id, f"Текст для реклами збережено:\n\n{channel_message}", reply_markup=markup)
        start_ros = 0
        send_messages_to_users(message)
    elif message.text == 'Реферальна програма':
        bot.send_message(message.chat.id, '''
Не забувай про реферальну систему нашого бота!
За кожного користувача, якого ти приведеш, ти отримаєш +10 доступних каналів.
        ''', reply_markup=create_markup_referal())
    elif message.text == 'Створити реферальний код':
        with sq.connect("User_referal.db") as con:
            cur = con.cursor()
            cur.execute("SELECT name_referal, add_num, join_referal FROM user_referal WHERE user_id = ?",
                        (message.from_user.id,))
            result = cur.fetchone()
            if result:
                name_referal, add_num, join_referal = result
                print(
                    f"Користувач: {message.from_user.id} з username {message.from_user.username} реферальний код {name_referal} кількість приглашоних {add_num}")
                if join_referal == 0:
                    bot.send_message(message.chat.id,f'Ось ваш реферальний код:')
                    bot.send_message(message.chat.id,
                                     f'{name_referal}')
                    bot.send_message(message.chat.id,
                                     f'Кількість доступних каналів по рефералці: {add_num}. Ви ще не ввели реферальний код друга.')
                else:
                    bot.send_message(message.chat.id, f'Ось ваш реферальний код:')
                    bot.send_message(message.chat.id,
                                     f'{name_referal}')
                    bot.send_message(message.chat.id,
                                     f'Кількість доступних каналів по рефералці: {add_num}. Реферальний код, за яким ви приєдналися:')
                    bot.send_message(message.chat.id,
                                     f'{join_referal}.', reply_markup=create_markup_referal())
            else:
                add_user_to_db_ref(message.from_user.id, message)
                with sq.connect("User_referal.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT name_referal, add_num FROM user_referal WHERE user_id = ?",
                                (message.from_user.id,))
                    result = cur.fetchone()
                    name_referal, add_num = result
                    bot.send_message(message.chat.id, f'Ось ваш реферальний код:')
                    bot.send_message(message.chat.id,
                                     f'{name_referal}')
                    bot.send_message(message.chat.id,
                                     f'Кількість запрошених користувачів: {add_num}. Ви ще не ввели реферальний код друга.',
                                     reply_markup=create_markup_referal())
    elif message.text == 'Ввести реферальний код':
        with sq.connect("User_referal.db") as con:
            cur = con.cursor()
            cur.execute("SELECT join_referal FROM user_referal WHERE user_id = ?",
                        (message.from_user.id,))
            result = cur.fetchone()
            if result:
                join_referal = result[0]
                if join_referal == 0:
                    bot.send_message(message.chat.id,
                                 f'Введіть реферальний код користувача який вас пригласив:',
                                 reply_markup=markup_stop)

                else:
                    bot.send_message(message.chat.id,
                                     f'Ви вже ввели реферальний код: \n{join_referal}',
                                     reply_markup=markup)
            else:
                add_user_to_db_ref(message.from_user.id, message)
    elif message.text == 'Інформація':
        bot.send_message(message.chat.id, f'{Text[3]}', reply_markup=markup_info)
    elif message.text == 'Що таке Api-key?':
        bot.send_message(message.chat.id, f'{Text[0]}', reply_markup=markup)
        video_path = "IMG_7671.MP4"

        try:
            # Відкриваємо відеофайл у двійковому режимі
            with open(video_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="Ось приклад!")
            print(f"Відео успішно надіслано користувачеві {message.chat.id}.")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "Відеофайл не знайдено.")
            print("Помилка: Відеофайл не знайдено.")
        except Exception as e:
            bot.send_message(message.chat.id, "Не вдалося надіслати відео.")
            print(f"Помилка: {e}")
    elif message.text == 'Хто такий фрідж?':
        bot.send_message(message.chat.id, f'{Text[1]}', reply_markup=markup)
    elif message.text == 'Реклама':
        bot.send_message(message.chat.id, f'{Text[2]}', reply_markup=markup)
    elif start_ros == 1:
        channel_message = message.text
        bot.send_message(message.from_user.id, f"Текст для реклами збережено:\n\n{channel_message}",
                         reply_markup=markup)
        start_ros = 0
        send_messages_to_users(message)
    elif message.text == 'Назад':
        bot.send_message(message.chat.id, '<--', reply_markup=markup)
    else:
        with sq.connect("User_data.db") as con:
            cur = con.cursor()
            cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (message.chat.id,))
            num_buy = cur.fetchone()[0]
        if num_buy == 3:
            keyword = message.text
            bot.send_message(message.from_user.id, f"Пошукове слово збережено:\n\n{keyword}")
            with sq.connect("User_data.db") as con:
                cur = con.cursor()
                cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (message.chat.id,))
                cur.execute("""
                                UPDATE user_data
                                SET num_buy = 0, keyword = ?
                                WHERE user_id = ?
                            """, (message.text, message.from_user.id))
                con.commit()
            main_search(api_key, keyword, message)
        elif num_buy == 2:
            api_key = message.text
            bot.send_message(message.from_user.id, f"API ключ збережено:\n\n{api_key}")
            with sq.connect("User_data.db") as con:
                cur = con.cursor()
                cur.execute("SELECT num_buy FROM user_data WHERE user_id = ?", (message.chat.id,))
                cur.execute("""
                                UPDATE user_data
                                SET num_buy = 0, api_key = ?
                                WHERE user_id = ?
                            """, (message.text, message.from_user.id))
                con.commit()
        elif len(message.text) > 7:
            try:
                key = int(message.text)
                with sq.connect("User_referal.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT name_referal FROM user_referal;")
                    result = cur.fetchall()
                    with sq.connect("User_referal.db") as con1:
                        cur1 = con1.cursor()
                        cur1.execute("SELECT name_referal FROM user_referal WHERE user_id = ?",
                                     (message.from_user.id,))
                        result1 = cur1.fetchone()
                    for res in result:
                        if res[0] == key:
                            if result1[0] == key:
                                bot.send_message(message.chat.id,
                                                 f'Ви ввели свій код: \n{key}',
                                                 reply_markup=markup)
                                return
                            else:
                                cur.execute("""
                                                                UPDATE user_referal
                                                                SET join_referal = ?
                                                                WHERE user_id = ?
                                                            """, (key, message.from_user.id))
                                con.commit()
                                bot.send_message(message.chat.id,
                                                 f'Ви успішно підключились по коду: \n{key}',
                                                 reply_markup=markup)
                                with sq.connect("User_referal.db") as con:
                                    cur = con.cursor()
                                    cur.execute("""
                                                                                                UPDATE user_referal
                                                                                                SET add_num = add_num + 1
                                                                                                WHERE name_referal = ?""",
                                                (key,))
                                    con.commit()
                                return
                    bot.send_message(message.chat.id,
                                     f'Ви ввели не дійсний код: \n{key}',
                                     reply_markup=markup)
            except Exception as e:
                bot.send_message(message.chat.id, f'Не зрозуміле повідомлення: {message.text}', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f'Не зрозуміле повідомлення: {message.text}', reply_markup=markup)


channels_file = 'Chanels.txt'
processed_channels_file = 'Proccesedchanels.txt'  # Файл для хранения обработанных каналов
CHECKED_CHANNELS_FILE = 'checked_channels.txt'
INACTIVE_CHANNELS_FILE = 'Chanels.txt'

def process_channels(message, buy):
    if buy:
        with sq.connect("Chanels_base.db") as con:
            cur = con.cursor()

            # Отримуємо дані користувача
            cur.execute("SELECT num_newchanel FROM users WHERE id = ?", (message.from_user.id,))
            user_data = cur.fetchone()
            if not user_data:
                bot.send_message(message.chat.id, "Виникла помилка. Будь ласка, спробуйте ще раз.")
                return

            num_newchanel = user_data[0]

            # Читаємо всі канали з файлу
            channels = get_all_channels()

            # Перевіряємо, чи є ще доступні канали
            if not channels:
                bot.send_message(message.chat.id, "На жаль, канали для обробки закінчилися. Спробуйте пізніше.")
                return

            # Отримуємо перший канал
            channel_line = channels[0]
            channel_parts = channel_line.split(',')
            if len(channel_parts) < 2:  # Перевірка формату
                bot.send_message(message.chat.id, "Сталася помилка з даними каналу. Зверніться до адміністратора.")
                return

            channel_id = channel_parts[0].strip()
            channel_name = channel_parts[1].strip()
            youtube_link = f'https://www.youtube.com/channel/{channel_id}'

            # Відправляємо канал користувачу
            bot.send_message(
                message.chat.id,
                f"Канал: {channel_name}\nПосилання: {youtube_link}"
            )
            # Відправляємо повідомлення з випадковим текстом
            bot.send_message(message.chat.id, get_random_message(channel_name), reply_markup=markup)

            # Видаляємо канал з основного файлу та додаємо в оброблені
            update_channel_files(channel_line)

            # Оновлюємо кількість виданих каналів користувачем у базі
            cur.execute("""
                UPDATE users
                SET num_newchanel = num_newchanel + 1
                WHERE id = ?
            """, (message.from_user.id,))
            con.commit()
    else:
        with sq.connect("Chanels_base.db") as con:
            cur = con.cursor()

            # Отримуємо дані користувача
            cur.execute("SELECT num_newchanel FROM users WHERE id = ?", (message.from_user.id,))
            user_data = cur.fetchone()
            if not user_data:
                bot.send_message(message.chat.id, "Виникла помилка. Будь ласка, спробуйте ще раз.")
                return

            num_newchanel = user_data[0]

            # Читаємо всі канали з файлу
            channels = get_all_channels()

            # Перевіряємо, чи є ще доступні канали
            if not channels:
                bot.send_message(message.chat.id, "На жаль, канали для обробки закінчилися. Спробуйте пізніше.")
                return

            # Отримуємо перший канал
            channel_line = channels[random.randint(0, len(channels) - 1)]
            channel_parts = channel_line.split(',')
            if len(channel_parts) < 2:  # Перевірка формату
                bot.send_message(message.chat.id, "Сталася помилка з даними каналу. Зверніться до адміністратора.")
                return

            channel_id = channel_parts[0].strip()
            channel_name = channel_parts[1].strip()
            youtube_link = f'https://www.youtube.com/channel/{channel_id}'

            # Відправляємо канал користувачу
            bot.send_message(
                message.chat.id,
                f"Канал: {channel_name}\nПосилання: {youtube_link}"
            )
            # Відправляємо повідомлення з випадковим текстом
            bot.send_message(message.chat.id, get_random_message(channel_name), reply_markup=markup)

            # Оновлюємо кількість виданих каналів користувачем у базі
            cur.execute("""
                UPDATE users
                SET num_newchanel = num_newchanel + 1
                WHERE id = ?
            """, (message.from_user.id,))
            con.commit()

# Функция для получения следующего канала из файла
def get_all_channels():
    try:
        with open(channels_file, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines() if line.strip()]  # Видаляємо порожні рядки
    except FileNotFoundError:
        print("Файл з каналами не знайдено.")
        return []
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        return []



# Функция для обновления файлов каналов
def update_channel_files(channel_line):
    global channels_file, processed_channels_file
    try:
        # Видаляємо рядок з основного файлу
        with open(channels_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(channels_file, 'w', encoding='utf-8') as file:
            for line in lines:
                if line.strip() != channel_line.strip():
                    file.write(line)

        # Додаємо рядок до файлу оброблених каналів
        with open(processed_channels_file, 'a', encoding='utf-8') as processed_file:
            processed_file.write(channel_line + '\n')

    except Exception as e:
        print(f"Помилка оновлення файлів: {e}")


def load_checked_channels():
    if not os.path.exists(CHECKED_CHANNELS_FILE):
        print("Файл перевірених каналів не знайдено. Створюється новий.")
        return set()
    with open(CHECKED_CHANNELS_FILE, 'r') as file:
        channels = set(line.strip() for line in file)
        return channels

def save_checked_channel(channel_id):
    with open(CHECKED_CHANNELS_FILE, 'a', encoding='utf-8') as file:
        file.write(channel_id + '\n')

def save_inactive_channel(channel_id, title, subscriber_count, total_watch_hours, message):
    with open(INACTIVE_CHANNELS_FILE, 'a', encoding='utf-8') as file:
        file.write(f"{channel_id}, {title}, {subscriber_count}, {total_watch_hours} годин\n")
        print(f"Неактивний канал збережено: {title} (ID: {channel_id}), підписників: {subscriber_count}, годин перегляду: {total_watch_hours}")
        bot.send_message(message.chat.id, f"Неактивний канал збережено. Ви отримали +1 до доступу.")
        with sq.connect("User_chanel.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO user_chanel (user_id, name_chanel, id_chanel) VALUES (?, ?, ?)", (message.chat.id, str(title), str(channel_id)))
            con.commit()
        with sq.connect("Chanels_base.db") as con:
            cur = con.cursor()
            # Отримуємо значення num_buy для користувача
            cur.execute("SELECT searchchannels FROM users WHERE id = ?", (message.from_user.id,))
            searchchannels = cur.fetchone()[0]
            cur.execute("""
                            UPDATE users
                            SET searchchannels = searchchannels + 1
                            WHERE id = ?
                        """, (message.from_user.id,))
            con.commit()

def count_inactive_channels():
    if not os.path.exists(INACTIVE_CHANNELS_FILE):
        return 0
    with open(INACTIVE_CHANNELS_FILE, 'r', encoding='utf-8') as file:
        return sum(1 for _ in file)

def get_video_statistics(video_id, api_key):
    url = f'https://www.googleapis.com/youtube/v3/videos?key={api_key}&id={video_id}&part=statistics'
    response = requests.get(url)
    return response.json().get('items', [{}])[0].get('statistics', {})

def get_watch_hours_for_last_active_year(videos, last_video_date, api_key):
    total_watch_hours = 0
    one_year_period = last_video_date - timedelta(days=365)

    for video in videos:
        published_at = video['snippet']['publishedAt']
        published_time = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')

        if not (one_year_period <= published_time <= last_video_date):
            continue

        video_id = video['id']['videoId']
        video_stats = get_video_statistics(video_id, api_key)
        view_count = int(video_stats.get('viewCount', 0))

        avg_watch_time_minutes = 5
        watch_hours = (view_count * avg_watch_time_minutes) / 60
        total_watch_hours += watch_hours

    return total_watch_hours

def check_channel_activity(youtube, channel_id, checked_channels, api_key, message):
    try:
        start_time = time.time()  # Запускаем таймер

        if time.time() - start_time > 30:
            return None, "timeout"

        channel_info = youtube.channels().list(
            part="statistics,snippet",
            id=channel_id
        ).execute()

        if not channel_info["items"]:
            return None, None

        statistics = channel_info["items"][0]["statistics"]
        title = channel_info["items"][0]["snippet"]["title"]
        subscriber_count = int(statistics["subscriberCount"])

        save_checked_channel(channel_id)

        if subscriber_count < 1000:
            return None, None

        videos = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            order="date",
            type="video"
        ).execute()

        if not videos["items"]:
            return None, None

        last_video_date = videos["items"][0]["snippet"]["publishedAt"]
        last_video_date = datetime.strptime(last_video_date, '%Y-%m-%dT%H:%M:%SZ')
        one_year_ago = datetime.now() - timedelta(days=365)

        total_watch_hours = get_watch_hours_for_last_active_year(videos['items'], last_video_date,
                                                                    youtube._developerKey)
        if total_watch_hours < 4000:
            return None, None
        if last_video_date < one_year_ago:
            save_inactive_channel(channel_id, title, subscriber_count, total_watch_hours, message)
            return title, subscriber_count

    except HttpError as e:
        if e.resp.status == 403 and "quota" in str(e):
            return None, "quota_reached"
        else:
            return None, "quota_None"
    return None, None

def search_channels_by_keyword(youtube, keyword, max_results):
    channel_ids = []
    next_page_token = None
    while len(channel_ids) < max_results:
        try:
            search_response = youtube.search().list(
                part='snippet',
                q=keyword,
                type='channel',
                maxResults=50,
                order='relevance',
                pageToken=next_page_token
            ).execute()

            channel_ids.extend(item['id']['channelId'] for item in search_response['items'])
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token:
                break
            print(len(channel_ids))

        except HttpError as e:
            if e.resp.status == 403 and "quota" in str(e):
                print("Досягнуто ліміту запитів до API під час пошуку каналів.")
                return channel_ids, "quota_reached"
            else:
                return channel_ids, "quota_None"
    return channel_ids, None

def main_search(api_key, keyword, message):
    checked_channels = load_checked_channels()
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    print(f"Используется API ключ: {api_key}")
    print(f"Запуск пошуку з ключовим словом: {keyword}")

    bot.send_message(message.chat.id, f"Використовується API-ключ: {api_key} \nЗапуск пошуку за ключовим словом: {keyword}", reply_markup=markup_stop)

    bot.send_message(message.chat.id,
                     f"Зачекайте будь ласка",
                     reply_markup=markup_stop)
    all_channel_ids, quota_status = search_channels_by_keyword(youtube, keyword, 300)
    if quota_status == "quota_reached":
        bot.send_message(message.chat.id, "Через досягнення квоти API-ключа пошук зупинено.", reply_markup=markup)
    elif quota_status == "quota_None":
        bot.send_message(message.chat.id, "Неправильний API-ключ.", reply_markup=markup)


    for channel_id in all_channel_ids:
        status = check_channel_activity(youtube, channel_id, checked_channels, api_key, message)
        if status == "quota_reached" or status == "timeout":
            bot.send_message(message.chat.id, "Через досягнення квоти API-ключа пошук зупинено.", reply_markup=markup)
    bot.send_message(message.chat.id,
                     f"Пошук каналів припинено",
                     reply_markup=markup)
# Запуск бота
res = True
while res:
    try:
        bot.polling(skip_pending=True, none_stop=True)
        res = False
    except Exception as e:
        print(f"bot_stop: {e}")
        res = True

