import logging
from aiogram.utils import executor
from create_bot import dp
from data_base import sqlite_db # База данных
from data import data_db #Yclients
from scheduler import scheduler_options # Планировщик
#from scheduler.scheduler_options import BirthdayService
#import pandas as pd # Yclients

# Настройка логирования
logging.basicConfig(level=logging.INFO)

#Вывод сообщения в консоли
async def on_startup(_):
	print('Бот вышел в онлайн')
	sqlite_db.sql_newsletter() # Запуск базы данных акция
	sqlite_db.sql_services() # Запуск базы данных услуг
	#sqlite_db.sql_masters() # Запуск базы данных мастеров
	sqlite_db.sql_clients() # Запуск базы данных клиентов
	scheduler_options.setup_birthday_scheduler(_.bot, dp) # Планировщик 
	birthdays = await sqlite_db.get_todays_birthdays()

from handlers import client, admin

# Активируем наши хендлеры клиент, админ, другое
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)

# Функция корректного завершения работы
async def on_shutdown(dp):
    print('🛑 Останавливаем планировщик...')
    #service = BirthdayService(dp.bot, dp) # Если возникнут проблемы с планировщиком (дублирование сообщений)
    #service.scheduler.shutdown(wait=False) 
    print('✅ Планировщик остановлен')

# skip_updates в момент когда бот не онлайн он отвечать не будет
executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)