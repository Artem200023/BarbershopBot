from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_client
from aiogram.types import ReplyKeyboardRemove
from data_base import sqlite_db

# Создаем команды
#@dp.message_handler(commands=['start', 'help'])
# По вызову команд будут определенные сообщения
async def command_start(message:types.Message):
	await message.delete()
# try нужно для того что бы пользователь первый раз когда писал ему присылалсь ссылка на бота  - продолжение except:
	try:
# reply_markup=kb_client - переменная в которой находится клава
		await bot.send_message(message.from_user.id, 'Хорошего настроения !', reply_markup=kb_client)
# Удаляет команду написанную пользователем 
		#await message.delete()
	except:
		await message.reply('Общение с ботом через ЛС, напишите боту: \nhttps://t.me/BarberArtemBot')

#@dp.message_handler(lambda message:'Режим работы' in message.text)            #@dp.message_handler(commands=['Режим_работы'])
# По вызову команд будут определенные сообщения
async def c_open(message:types.Message):                                         #async def command_open(message:types.Message):
		await bot.send_message(message.from_user.id, 'Пн-Вс с 9:00 до 21:00')

#@dp.message_handler(lambda message:'Расположение' in message.text)		       #@dp.message_handler(commands=['Расположение'])
# По вызову команд будут определенные сообщения
async def c_place(message:types.Message):
	# reply_markup=ReplyKeyboardRemove() - при нажатии кнопки уходят на совсем
		await bot.send_message(message.from_user.id, 'ул. Ленина 90')#, reply_markup=ReplyKeyboardRemove())
#@dp.message_handler(lambda message: 'Меню' in message.text)
async def c_menu(message: types.Message):
	await sqlite_db.sql_read(message)


# Регистрируем хендлер и активируем его в главном коде
def register_handlers_client(dp:Dispatcher):
	dp.register_message_handler(command_start, commands=['start', 'help'])
	dp.register_message_handler(c_open, lambda message:'Режим работы' in message.text)
	dp.register_message_handler(c_place, lambda message:'Расположение' in message.text)
	dp.register_message_handler(c_menu, lambda message:'Меню' in message.text)