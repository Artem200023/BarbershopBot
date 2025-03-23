import logging
from aiogram.utils import executor
from create_bot import dp
from data_base import sqlite_db # База данных
from data import data_db #Yclients
#import pandas as pd # Yclients

# Настройка логирования
logging.basicConfig(level=logging.INFO)

#Вывод сообщения в консоли
async def on_startup(_):
	print('Бот вышел в онлайн')
	sqlite_db.sql_newsletter() # Запуск базы данных
	#sqlite_db.sql_masters() # Запуск базы данных мастеров
	sqlite_db.sql_clients() # Запуск базы данных клиентов

from handlers import client, admin

# Активируем наши хендлеры клиент, админ, другое
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)

# skip_updates в момент когда бот не онлайн он отвечать не будет
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)