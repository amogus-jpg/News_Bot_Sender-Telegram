import requests
from telegram import Bot
from telegram import ParseMode
from telegram.ext import Updater

from newsdataapi import NewsDataApiClient

# Для API ключа, зарегистрируйтесь на https://newsdata.io
api = NewsDataApiClient(apikey='')

# Токен бота Telegram
TOKEN = ''

# Идентификатор канала (после ссылки с "@" идёт ваш ID канала)
CHANNEL_ID = ''

bot = Bot(token=TOKEN)

def Drop_News():
  # Для изменения параметров вызова API, обратитесь к документации https://newsdata.io/documentation/#latest-news
  response = api.news_api(country='ru', size=1)
  
  message = '*' + response['results'][0]['title'] + '*' + '\n' + '\n' + response['results'][0]['content']
  bot.sendMessage(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN)

def Program():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Вызов функции send_news в канал с CHANNEL_ID и с интервалом 2 часа
    updater.job_queue.run_repeating(send_news, interval=7200, first=0, context=CHANNEL_ID)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    Program()
