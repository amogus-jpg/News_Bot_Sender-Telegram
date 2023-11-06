# Импортированные библиотеки
import re
import time
import threading
import configparser
import sys
import pypresence
import ctypes
from telegram import Bot
from telegram import ParseMode
from telegram.ext import Updater
from newsdataapi import NewsDataApiClient

# Загрузка конфигурации из файла config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Получение API ключа и токена бота из конфигурации
api_key = config['API']['api_key']
TOKEN = config['Bot']['token']
CHANNEL_ID = config['Channel']['channel_id']
Discord_Presence_Decision = config.getboolean('Allow_Discord_Presence', 'decision')
CLIENT_ID = config['Discord_Client_ID']['application_id']

# Для API ключа, зарегистрируйтесь на https://newsdata.io
api = NewsDataApiClient(apikey=api_key)

# Вход в бота
bot = Bot(token=TOKEN)

# Задайте новый заголовок для консоли
new_title = "Running code for Telegram channel: " + CHANNEL_ID
ctypes.windll.kernel32.SetConsoleTitleW(new_title)

# Функция для отправки сообщения в Telegram
def send_message(text):
    bot.sendMessage(chat_id=CHANNEL_ID, text=text, parse_mode=ParseMode.MARKDOWN)

# Функция для запуска секундомера
def start_stopwatch():
    seconds = 0
    minutes = 0
    hours = 0

    while True:
        time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
        sys.stdout.write("\rВремя текущей сессии: " + time_string)
        sys.stdout.flush()

        seconds += 1
        if seconds == 60:
            seconds = 0
            minutes += 1
        if minutes == 60:
            minutes = 0
            hours += 1

        time.sleep(1)

# Функция для проверки текста на наличие только русских, английских букв, цифр и пробелов
def contains_only_russian_or_english_or_numbers(text):
    pattern = r'^[а-яА-Яa-zA-Z0-9\s]+$'
    return bool(re.match(pattern, text))

# Функция для получения новостей и отправки их в канал
def drop_news(garbage):
    response = api.news_api(country='ru', size=1)
    title = response['results'][0]['title']
    content = response['results'][0]['content']

    if contains_only_russian_or_english_or_numbers(title) and contains_only_russian_or_english_or_numbers(content):
        message = '*' + title + '*' + '\n' + content
        send_message(message)
    else:
        error_message = "К сожалению, мы не смогли выложить для вас новость.\n\nВозможно, в заголовке или в содержимом не было ничего, либо содержало какие-либо символы, противоречащие поиску.\n\nСледующую новость опубликуем спустя 1 час и 30 минут."
        bot.send_message(chat_id=CHANNEL_ID, text=error_message, parse_mode=ParseMode.MARKDOWN, disable_notification=True)

def program():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Запустить секундомер в отдельном потоке
    stopwatch_thread = threading.Thread(target=start_stopwatch)
    stopwatch_thread.daemon = True
    stopwatch_thread.start()
    
    if Discord_Presence_Decision:
        # Создайте экземпляр клиента Discord Rich Presence
        RPC = pypresence.Presence(client_id=CLIENT_ID)
        RPC.connect()

        RPC.update(
            state="Текст",
            details="Текст",
            large_image='Изображение большой иконки',
            large_text="Текст",
            small_image='Изображение маленькой иконки',
            small_text='Текст'
        )

    # Отправлять новости каждые 1 час и 30 минут
    updater.job_queue.run_repeating(drop_news, interval=5400, first=0, context=CHANNEL_ID)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    program()