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
  response = api.news_api(country='ru', size=1)
  message = '*' + response['results'][0]['title'] + '*' + '\n' + '\n' + response['results'][0]['content']
  bot.sendMessage(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN)

def Program():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    updater.job_queue.run_repeating(Drop_News, interval=10, first=0, context=CHANNEL_ID)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    Program()
