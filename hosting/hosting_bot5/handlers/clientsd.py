from aiogram.dispatcher import FSMContext # Для того что бы работала последовательность (машина состояний)
from aiogram.dispatcher.filters.state import State, StatesGroup # Машина состояний
from aiogram import types, Dispatcher
from create_bot import dp, bot, api
from keyboards import client_kb
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from data_base import sqlite_db
from danniey import popitka_db
from aiogram.dispatcher.filters import Text
#from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar
from aiogram_calendar_rus import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar

import json # Пробник
#from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#import asyncio #, time

admin = 1123330844
adresa = ['пр. Ленина, 90', 'Фрунзе 105']

# Создаем команды
#@dp.message_handler(commands=['start', 'help'])
# По вызову команд будут определенные сообщения
async def command_start(message:types.Message):
	#time.sleep(0.3) #time
	#await asyncio.sleep(1) # Задержка 
# try нужно для того что бы пользователь первый раз когда писал ему присылалсь ссылка на бота  - продолжение except:
	try:
# reply_markup=kb_client - переменная в которой находится клава              
		await bot.send_message(message.from_user.id, 'Хорошего настроения !', reply_markup=client_kb.kb_client)
# Удаляет команду написанную пользователем 
		#await message.delete()
	except:
		await message.reply('Общение с ботом через ЛС, напишите боту: \nhttps://t.me/BarberArtemBot')
	await message.delete()
#@dp.message_handler(lambda message:'Режим работы' in message.text)            #@dp.message_handler(commands=['Режим_работы'])
# По вызову команд будут определенные сообщения
async def c_open(message:types.Message):                                         #async def command_open(message:types.Message):
	await bot.send_message(message.from_user.id, 'Пн-Вс с 10:00 до 21:00')

#@dp.message_handler(lambda message:'Расположение' in message.text)		       #@dp.message_handler(commands=['Расположение'])
# По вызову команд будут определенные сообщения
async def c_place(message:types.Message):
	# reply_markup=ReplyKeyboardRemove() - при нажатии кнопки уходят на совсем
	await bot.send_message(message.from_user.id, 'ул. Ленина 90, Фрунзе 105')#, reply_markup=ReplyKeyboardRemove())

#@dp.message_handler(lambda message: 'Меню' in message.text)
async def c_menu(message: types.Message):
	await sqlite_db.sql_read(message)
#----------------------------------------------------

#@dp.message_handler(commands='Refresh')            
# По вызову команд будут определенные сообщения
async def c_refresh(message:types.Message):                                         
	await message.answer('Обновлено !', reply_markup=ReplyKeyboardRemove())
	await message.delete() 

#-------------------------------Машина состояний записаться на стрижку---------------------------------------

class FSMClient(StatesGroup):
	fio = State()
	phone = State()
	master = State()
	striga = State()
	#adres = State()
	#master = State()
	date = State()
	time = State()

# Начало диалога загрузки нового пункта меню
#@dp.message_handler(lambda message:'Записаться на стрижку' in message.text, state=None) 
async def cm_zapis(message: types.Message):
	await FSMClient.fio.set()
	await message.answer('Напишите ваше имя:', reply_markup=client_kb.kb_otmena)

#Выход из состояний
#@dp.message_handler(state="*", commands= 'Отмена')
#@dp.message_handler(Text(equals='Отмена', ignore_case=True), state="*")
async def otmena_handler(message: types.Message, state: FSMContext):
	#current_state = await state.get_state()
	#if current_state is None:
		#return
	await state.finish()
	await message.reply('Отменил', reply_markup=client_kb.kb_client)

#Ловим первый ответ от пользователя и пишем в словарь
#@dp.message_handler(state=FSMClient.fio)
async def cm_fio(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['fio'] = message.text
	await FSMClient.next()
	await message.answer('Укажите ваш номер телефона :', reply_markup=client_kb.kb_phone)

#Ловим второй ответ
#@dp.message_handler(content_types=types.ContentType.CONTACT, state=FSMClient.phone) # Это что бы принимать только по кнопке
#async def cm_phone(message: types.Message, state: FSMContext): # Связанно с первым 
#@dp.message_handler(content_types=['contact', 'text'], state=FSMClient.phone)
async def cm_phone(message: [types.Contact, types.Message], state: FSMContext):
	async with state.proxy() as data:
		data['phone'] = message.contact.phone_number if message.contact else message.text
	await FSMClient.next()
	await message.answer('Выберите мастера :', reply_markup=client_kb.kb_otmena) # reply_markup=ReplyKeyboardRemove()) Удалять кнопки
	#read = await sqlite_db.sql_readlenina()
	# all_staff = api.get_staff()
 	
	# for ret in all_staff['data']:  
	# 	await bot.send_message(message.from_user.id, f"{ret['name']}\n{ret['specialization']}\n {ret['avatar']}", reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f"Выбрать  {ret['name']}", callback_data=f"master {str(ret['id'])}")))
#--------------------------------------------------------------- Пробник
	read = await sqlite_db.sql_readlenina()
	for ret in read:  
		#await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\n{ret[2]}',reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Выбрать {ret[1]}', callback_data=f'master {ret[1]}')))
		msg = await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\n{ret[2]}',reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Выбрать {ret[1]}', callback_data=f'master {ret[1]}')))
		#await msg.delete()
#---------------------------------------------------------------
#Ловим пятый ответ
#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('master '), state=FSMClient.master)
async def cm_master(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		#await msg.delete()
		#await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
		await call.message.delete() # Правильный
		data['master'] = call.data.replace(f"master ","")
		await call.message.answer(f"Вы выбрали {data['master']} ✅", reply_markup=client_kb.kb_otmena)
		#data['master'] = call.data.replace(f"master ","") 
	await FSMClient.next()

	await call.message.answer('Выберите услугу :', reply_markup=client_kb.kb_otmena)
#--------------------------------------------------------------- Пробник
	read = await sqlite_db.sql_readlenina()
	for ret in read:  
		await call.bot.send_photo(call.message.chat.id, ret[0], f'{ret[1]}\n{ret[2]}',reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Выбрать {ret[1]}', callback_data=f'service {ret[1]}')))
#---------------------------------------------------------------
	# staff_id = data['master']
	# services = api.get_services(staff_id=staff_id)

	# for ret in services['data']['services']: 
	# 	await call.message.answer(f"{ret['title']} - {str(ret['price_min'])} руб.", reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f"Выбрать  {ret['title']}", callback_data=f"service {ret['id']}"))) #f"service {ret['title']}")))

#Ловим третий ответ
#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('service '), state=FSMClient.striga)
async def cm_striga(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		#data['striga'] = call.message.text
		await call.message.delete()
		data['striga'] = call.data.replace(f"service ","") #message.text
		await call.message.answer(f"Вы выбрали {data['striga']} ✅", reply_markup=client_kb.kb_otmena)
	await FSMClient.next()
	with open('data1.json', 'r', encoding='utf-8') as f:
		all_staff = json.load(f)
		day = all_staff['data'].get('booking_dates')
		new_str1 = '\n'.join([f"📅 {item}" for item in day])
		await call.message.answer(f"Выберите дату :\n{new_str1}", reply_markup=await SimpleCalendar().start_calendar())

	# await call.message.answer('Выберите дату :', reply_markup=await SimpleCalendar().start_calendar())
#-----------------------------------------------------------------------------------------------------------
	#staff_id = data['master']
	#service_id = data['striga']
	#booking_days = api.get_available_days(staff_id=staff_id, service_id=service_id)


	#print(booking_days)

	#day = booking_days['data'].get('booking_dates')  # or .get('booking_days')
	#day = booking_days['data'].get('booking_dates') --------------
	#print(*day, sep='\n')
	#newline = '\n' --------------------
	#await call.message.answer(f"{*day, sep='\n'}")
	#await call.message.answer(f"{newline}{' '.join(day)}.{newline}") -----------------
	
	# #await call.message.answer(f"Даты :\n{booking_days}")
	#for ret in booking_days['data'].dumps('booking_dates'):
		#await call.message.answer(f"{object(ret['booking_dates'])}", reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f"Выбрать дату", callback_data=f"date1 стр"))) 

#-------------------------------------------------------------------------------------------------------------
	#await call.message.answer('Выберите дату :', reply_markup=await SimpleCalendar().start_calendar())

#@dp.callback_query_handler(simple_cal_callback.filter(), state=FSMClient.date)
async def cm_date(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
	async with state.proxy() as data:
		selected, date = await SimpleCalendar().process_selection(call, callback_data)
		if selected:
			with open('data1.json', 'r', encoding='utf-8') as f:
				all_staff = json.load(f)
				day = all_staff['data'].get('booking_dates')
            
				if date.strftime("%d-%m-%Y") in day:
					await call.message.delete()
					data['date'] = date.strftime("%d-%m-%Y")
					await call.message.answer("Выберите дату :") 
					await call.message.answer(f'Вы выбрали {date.strftime("%d-%m-%Y")} ✅', reply_markup=client_kb.kb_otmena)
					#---------------------------------------- Пробник (Здесь остановился) (Вроде все хорошо)
					with open('data2.json', 'r', encoding='utf-8') as f:
						time_slots = json.load(f)
						new_str = '\n'.join([f"{ret['time']}" for ret in time_slots['data']])
						#new_str1 = '\n'.join([f"⏰{ret['time']}" for ret in time_slots['data']])
						result = new_str.split()
						keyboard = types.InlineKeyboardMarkup(row_width=2)
						buttons = []
						for i, item in enumerate(result):
							num = types.InlineKeyboardButton(text=f'{item}', callback_data=f'time1 {item}')
							buttons.insert(i, num)
						keyboard.add(*buttons)
						await call.bot.send_message(call.message.chat.id, f"Выберите время :\n", reply_markup=keyboard)
		
					#----------------------------------------
					# await call.message.answer('Выберите время', reply_markup=client_kb.kb_otmena)
				else:
					await call.message.delete()
					day = all_staff['data'].get('booking_dates')
					new_str1 = '\n'.join([f"📅 {item}" for item in day])
					await call.message.answer(f'Данной даты нет в расписании у мастера, выберите дату указанную ниже ❌\n{new_str1}', reply_markup=await SimpleCalendar().start_calendar())
					await FSMClient.previous()
				await FSMClient.next()
	
	#await FSMClient.next()
	
	#await call.message.answer('Выберите время :', reply_markup=client_kb.kb_otmena)

	# staff_id = data['master']
	# service_id = data['striga']
	# day = data['date']

	# time_slots = api.get_available_times(staff_id=staff_id, service_id=service_id, day=day)
	# #print(time_slots)
	# for ret in time_slots['data']: 
	# 	await call.message.answer(f"{ret['time']}", reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f"{ret['time']}", callback_data=f"time1 {ret['datetime']}"))) #f"service {ret['title']}")))

#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('time1 '), state=FSMClient.time)
async def cm_time(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		with open('data2.json', 'r', encoding='utf-8') as f:
			time_slots = json.load(f)
			new_str = '\n'.join([f"{ret['time']}" for ret in time_slots['data']])
			if call.data.replace("time1 ", "") in new_str:
				data['time'] = call.data.replace(f"time1 ","")
				await call.message.delete()
				await call.message.answer("Выберите время :")
				await call.message.answer(f'Вы выбрали {call.data.replace("time1 ", "")} ✅')
			else: 
				#await call.message.delete()
				await call.message.answer(f'Время занято, выберите время из ниже указанного ❌\n{new_str}', reply_markup=client_kb.kb_otmena)
				await FSMClient.previous()

		await call.message.answer('Вы успешно записаны !', reply_markup=client_kb.kb_client)
		await call.bot.send_message(admin, f"Поступила запись !\nИмя: {data['fio']}\nТелефон: {data['phone']}\nМастер: {data['master']}\nУслуга: {data['striga']}\nДата: {data['date']}\nВремя: {data['time']}")
	await state.finish()

	#date_time = time_slots['data'].get('time')  # or .get('datetime')
#--------------------------------------------------------------------------
#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('date1 '), state=FSMClient.date)
# async def cm_date(call: types.CallbackQuery, state: FSMContext):
# 	async with state.proxy() as data:
# 		data['date'] = call.data.replace(f"date1 ","") 
# 	await FSMClient.next()
# 	await call.message.answer('Выберите время :', reply_markup=client_kb.kb_otmena)

#--------------------------------------------------------------

		#, reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f"Выбрать  {ret['title']}", callback_data=f"service {ret['id']}"))) #f"service {ret['title']}")))

	# for ret in booking_days['data']: 
	# 	await call.message.answer(f"{ret['title']}\n{str(ret['price_min'])}", reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f"Выбрать  {ret['title']}", callback_data=f"service {ret['id']}"))) #f"service {ret['title']}")))


#Ловим четвертый ответ
#@dp.message_handler(state=FSMClient.adres)
# async def cm_adres(message: types.Message, state: FSMContext):
# 	async with state.proxy() as data:
# 		data['adres'] = message.text
# 	await FSMClient.next()

# 	if message.text in adresa:
# 		await message.answer('Выберите мастера :', reply_markup=client_kb.kb_otmena)

# 		if data['adres'] == 'пр. Ленина, 90':
# 			read = await sqlite_db.sql_readlenina()
	
# 		elif data['adres'] == 'Фрунзе 105':
# 			read = await sqlite_db.sql_readfrynze()

# 		for ret in read:  
# 			await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\n{ret[2]}',reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Выбрать {ret[1]}', callback_data=f'master {ret[1]}')))
# 			#await bot.send_message(message.from_user.id, text='Нажми на кнопку ниже !', reply_markup=client_kb.kb_case_inline)

# 	else:
# 		await message.answer('Дружище выбрать нужно из кнопок !')
# 		await FSMClient.previous()

#Ловим седьмой ответ
# #@dp.message_handler(state=FSMClient.time)
# async def cm_time(message: types.Message, state: FSMContext):
# 	async with state.proxy() as data:
# 		data['time'] = message.text
# 	await message.answer('Вы успешно записаны !', reply_markup=client_kb.kb_client)
# 	await bot.send_message(admin, f"Поступила запись !\nИмя: {data['fio']}\nТелефон: {data['phone']}\nМастер: {data['master']}\nСтрижка: {data['striga']}\nДата: {data['date']}\nВремя: {data['time']}")
	
# 	#await call.message.answer("Вы успешно записаны !", reply_markup=client_kb.kb_client)
# 	#await call.bot.send_message(admin, 'Поступила запись !\n' +'Имя: ' +data['fio'] +'\nТелефон: ' +data['phone'] +'\nСтрижка: ' +data['striga'] +'\nАдрес: ' +data['adres'] +'\nМастер: ' +data['master'] ) #await call.bot.send_message(admin, 'Поступила запись !', f'\nИмя: {data['fio']}\nТелефон: {data['phone']}\nСтрижка: {data['striga']}') 	
# 	#await call.bot.send_message(admin, text=f"Поступила запись ! {data['fio'], data['phone'], data['striga']}")
# 	#await call.bot.send_message(admin, 'Поступила запись !', f'\nИмя: {data["fio"]}\nТелефон: {data["phone"]}\nСтрижка: {data["striga"]}')
# 	await state.finish()

#----------------------------------------------------------------------------------------------------------------

# Регистрируем хендлер и активируем его в главном коде
def register_handlers_client(dp:Dispatcher):
	dp.register_message_handler(command_start, commands=['start', 'help'])
	dp.register_message_handler(c_open, lambda message:'Режим работы' in message.text)
	dp.register_message_handler(c_place, lambda message:'Расположение' in message.text)
	dp.register_message_handler(c_menu, lambda message:'Меню' in message.text)
	dp.register_message_handler(c_refresh, commands='Refresh')
	#----------------------------Хендлеры записаться на стрижку--------------------------------
	dp.register_message_handler(cm_zapis, lambda message:'Записаться на стрижку' in message.text, state=None)
	dp.register_message_handler(otmena_handler, state="*", commands='Отмена')
	dp.register_message_handler(otmena_handler, Text(equals='Отмена', ignore_case=True), state="*")
	dp.register_message_handler(cm_fio, state=FSMClient.fio)
	dp.register_message_handler(cm_phone, content_types=['contact', 'text'], state=FSMClient.phone)
	dp.register_callback_query_handler(cm_master, lambda x: x.data and x.data.startswith("master "), state=FSMClient.master)
	dp.register_callback_query_handler(cm_striga, lambda x: x.data and x.data.startswith("service "), state=FSMClient.striga)
	#dp.register_message_handler(cm_adres, state=FSMClient.adres)
	dp.register_callback_query_handler(cm_date, simple_cal_callback.filter(), state=FSMClient.date)
	dp.register_callback_query_handler(cm_time, lambda x: x.data and x.data.startswith('time1 '), state=FSMClient.time)

