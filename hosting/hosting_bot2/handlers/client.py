from aiogram.dispatcher import FSMContext # Для того что бы работала последовательность (машина состояний)
from aiogram.dispatcher.filters.state import State, StatesGroup # Машина состояний
from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_client, kb_phone, kb_otmena
from aiogram.types import ReplyKeyboardRemove
from data_base import sqlite_db
from aiogram.dispatcher.filters import Text
#import asyncio #time

admin = 1123330844

class FSMClient(StatesGroup):
	fio = State()
	phone = State()
	striga = State()

# Создаем команды
#@dp.message_handler(commands=['start', 'help'])
# По вызову команд будут определенные сообщения
async def command_start(message:types.Message):
	#time.sleep(0.3) #time
	#await asyncio.sleep(1) # Задержка 
# try нужно для того что бы пользователь первый раз когда писал ему присылалсь ссылка на бота  - продолжение except:
	try:
# reply_markup=kb_client - переменная в которой находится клава
		await bot.send_message(message.from_user.id, 'Хорошего настроения !', reply_markup=kb_client)
# Удаляет команду написанную пользователем 
		#await message.delete()
	except:
		await message.reply('Общение с ботом через ЛС, напишите боту: \nhttps://t.me/BarberArtemBot')
	await message.delete()
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

#@dp.message_handler(lambda message:'ОбновитьRef' in message.text)            
# По вызову команд будут определенные сообщения
async def c_refresh(message:types.Message):                                         
	await bot.send_message(message.from_user.id, 'Обновлено !', reply_markup=ReplyKeyboardRemove())
	await message.delete()

# ------------------------------Машина состояний записаться на стрижку---------------------------------------
	
# Начало диалога загрузки нового пункта меню
#@dp.message_handler(lambda message:'Записаться на стрижку' in message.text, state=None) 
async def cm_zapis(message: types.Message):
	await FSMClient.fio.set()
	await message.answer('Напиши свое имя:', reply_markup=kb_otmena)

#Выход из состояний
#@dp.message_handler(state="*", commands= 'Отмена')
#@dp.message_handler(Text(equals='Отмена', ignore_case=True), state="*")
async def otmena_handler(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await state.finish()
	await message.reply('Отменил', reply_markup=kb_client)

#Ловим первый ответ от пользователя и пишем в словарь
#@dp.message_handler(state=FSMClient.fio)
async def cm_fio(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['fio'] = message.text
	await FSMClient.next()
	await message.answer("Напиши свой номер телефона:", reply_markup=kb_phone)

#Ловим второй ответ
#@dp.message_handler(state=FSMClient.phone)
async def cm_phone(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['phone'] = message.text
	await FSMClient.next()
	await message.answer("Как будем стричься?:", reply_markup=kb_otmena) # reply_markup=ReplyKeyboardRemove()) Удалять кнопки

#Ловим третий ответ
#@dp.message_handler(state=FSMClient.striga)
async def cm_striga(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['striga'] = message.text
		await message.answer("Вы успешно записаны !", reply_markup=kb_client)
		#await bot.send_message(admin, f'Поступила запись !\nИмя: {data[fio]}\nТелефон: {data['phone']}\nСтрижка: {data['striga']}')  #str(data))
		await bot.send_message(admin, 'Поступила запись !\n' +'Имя: ' +data['fio'] +'\nТелефон: ' +data['phone'] +'\nСтрижка: ' +data['striga'])	
	
	await state.finish()

#----------------------------------------------------------------------------------------------------------------

# Регистрируем хендлер и активируем его в главном коде
def register_handlers_client(dp:Dispatcher):
	dp.register_message_handler(command_start, commands=['start', 'help'])
	dp.register_message_handler(c_open, lambda message:'Режим работы' in message.text)
	dp.register_message_handler(c_place, lambda message:'Расположение' in message.text)
	dp.register_message_handler(c_menu, lambda message:'Меню' in message.text)
	dp.register_message_handler(c_refresh, lambda message:'ОбновитьRef' in message.text)
	dp.register_message_handler(cm_zapis, lambda message:'Записаться на стрижку' in message.text, state=None)
	dp.register_message_handler(otmena_handler, state="*", commands='Отмена')
	dp.register_message_handler(otmena_handler, Text(equals='Отмена', ignore_case=True), state="*")
	dp.register_message_handler(cm_fio, state=FSMClient.fio)
	dp.register_message_handler(cm_phone, state=FSMClient.phone)
	dp.register_message_handler(cm_striga, state=FSMClient.striga)
