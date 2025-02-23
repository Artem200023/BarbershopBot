from aiogram.utils import executor
from create_bot import dp
from data_base import sqlite_db # База данных

import json, string  #import os


#Вывод сообщения в консоли
async def on_startup(_):
	print('Бот вышел в онлайн')
	sqlite_db.sql_start() # База данных

from handlers import client, admin, other

# Активируем наши хендлеры клиент, другое
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
other.register_handlers_other(dp)


# skip_updates в момент когда бот не онлайн он отвечать не будет
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)