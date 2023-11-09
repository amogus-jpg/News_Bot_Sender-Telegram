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

# Глобальная переменная для определения, следует ли продолжать работу с секундомером
continue_stopwatch = True

# Переменные для запоминания последних полученных данных
lastTitle = ''
lastContent = ''

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

    while continue_stopwatch:
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

# Функция для получения новостей и отправки их в канал
def drop_news(garbage):
    global lastTitle
    global lastContent

    response = api.news_api(country='ru', size=1, language='ru')
    title = response['results'][0]['title']
    content = response['results'][0]['content']

    if not title == lastTitle and not content == lastContent:
        
        lastTitle = title
        lastContent = content

        message = '*' + title + '*' + '\n' + content
    else:
        message = 'Новость, полученная ботом - повторилась.\nВозможно, новостей пока нет.\n\nЧерез 1 час и 30 минут должна появится новая новость.'

    send_message(message)

def discordrp():
    # Создайте экземпляр клиента Discord Rich Presence
    RPC = pypresence.Presence(client_id=CLIENT_ID)
    RPC.connect()

    # Цикл
    while True:
         # Установите текущее изображение в Discord Rich Presence
         RPC.update(
            state="",
            details="",
            large_image="",
            large_text="",
            small_image="",
            small_text=""
        )
        
         # Подождите 1.2 секунды перед обновлением
         time.sleep(1.25)

def program():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Запустить секундомер в отдельном потоке
    stopwatch_thread = threading.Thread(target=start_stopwatch)
    stopwatch_thread.daemon = True
    stopwatch_thread.start()

    if Discord_Presence_Decision:
        # Запустить DRP в отдельном потоке
        DRP_thread = threading.Thread(target=discordrp)
        DRP_thread.daemon = True
        DRP_thread.start()

    # Отправлять новости каждые 1 час и 30 минут
    updater.job_queue.run_repeating(drop_news, interval=5400, first=0, context=CHANNEL_ID)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    program()
