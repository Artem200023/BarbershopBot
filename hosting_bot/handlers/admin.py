from aiogram.dispatcher import FSMContext # Машина состояний
from aiogram.dispatcher.filters.state import State, StatesGroup # Машина состояний
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db # База данных
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ID = None

#-----------------------------------Машина состояний для загрузки в меню---------------------------------------------

class FSMAdmin(StatesGroup):
	photo = State()
	name = State()
	description = State()
	price = State()

# Код для управления ботом администратором
#@dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message:types.Message):
	global ID
	ID = message.from_user.id
	await bot.send_message(message.from_user.id, 'Что надо хозяин?', reply_markup=admin_kb.button_case_admin) # Другой способ добавления кнопки
	await message.delete()

# Начало диалога загрузки нового пункта меню
#@dp.message_handler(commands='Загрузить', state=None)
async def cm_start(message: types.Message):
	if message.from_user.id == ID: # Связь с адиминистратором
		await FSMAdmin.photo.set()
		await message.reply('Загрузи фото', reply_markup=admin_kb.button_case_otmenit)

#Выход из состояний
#@dp.message_handler (state="*", commands= 'Отменить')
#@dp.message_handler (Text(equals='Отменить', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		current_state = await state.get_state()
		if current_state is None:
			return
		await state.finish()
		await message.reply('Отменил', reply_markup=admin_kb.button_case_admin)

#Ловим первый ответ от пользователя и пишем в словарь
#@dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		async with state.proxy() as data:
			data['photo'] = message.photo[0].file_id
		await FSMAdmin.next()
		await message.reply("Теперь введи название")

#Ловим второй ответ
#@dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		async with state.proxy() as data:
			data['name'] = message.text
		await FSMAdmin.next()
		await message.reply("Введи описание")

#Ловим третий ответ
#@dp.message_handler(state=FSMAdmin.description)
async def load_description(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		async with state.proxy() as data:
			data['description'] = message.text
		await FSMAdmin.next()
		await message.reply("Теперь укажи цену")

#Ловим четвертый (последний) ответ
#@dp.message_handler(state=FSMAdmin.price)
async def load_price(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		async with state.proxy() as data:
			data['price'] = message.text # Было так float(message.text)
			await message.answer('Позиция добавлена !', reply_markup=admin_kb.button_case_admin)
	
	# База данныйх
		await sqlite_db.sql_add_command(state)
		await state.finish()

	# Этот код отправлял в телеграм id фото сообщением
		#async with state.proxy() as data:
			#await message.reply(str(data))
		#await state.finish()

#--------------------------------------------Инлайн кнопка удалить позицию------------------------------------------

#@dp.message_handler(commands='Удалить')
async def delete_item(message: types.Message):
	if message.from_user.id == ID:
		read = await sqlite_db.sql_read2()
		for ret in read:                                       
			#await bot.send_photo(message.from_user.id, ret[0], f'Название: {ret[1]}\nОписание: {ret[2]}\nЦена: {ret[-1]}')
			await bot.send_photo(message.from_user.id, ret[0], f'Название: {ret[1]}\nОписание: {ret[2]}\nЦена: {ret[-1]}', reply_markup=InlineKeyboardMarkup().\
				add(InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}')))

#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(call: types.CallbackQuery):
	await sqlite_db.sql_delete_command(call.data.replace('del ', ''))
	await call.answer(text=f'{call.data.replace("del ", "")} удалена.', show_alert=True)
	await call.message.delete()

#---------------------------------Машина состояний для загрузки мастеров---------------------------------------------

class FSMAdminMasters(StatesGroup):
	photo = State()
	name = State()
	exp = State()
	location = State()

# Код для управления ботом администратором
#@dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message:types.Message):
	global ID
	ID = message.from_user.id
	await bot.send_message(message.from_user.id, 'Что надо хозяин?', reply_markup=admin_kb.button_case_admin) # Другой способ добавления кнопки
	await message.delete()

# Начало диалога загрузки нового пункта меню
#@dp.message_handler(commands='Загрузить_мастера', state=None)
async def cm_start_m(message: types.Message):
	if message.from_user.id == ID: # Связь с адиминистратором
		await FSMAdminMasters.photo.set()
		await message.reply('Загрузи фото', reply_markup=admin_kb.button_case_otmenit)

#Выход из состояний
#@dp.message_handler (state="*", commands= 'Отменить')
#@dp.message_handler (Text(equals='Отменить', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		current_state = await state.get_state()
		if current_state is None:
			return
		await state.finish()
		await message.reply('Отменил', reply_markup=admin_kb.button_case_admin)

#Ловим первый ответ от пользователя и пишем в словарь
#@dp.message_handler(content_types=['photo'], state=FSMAdminMasters.photo)
async def load_photo_m(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		async with state.proxy() as data:
			data['photo'] = message.photo[0].file_id
		await FSMAdminMasters.next()
		await message.reply("Теперь введи имя мастера :")

#Ловим второй ответ
#@dp.message_handler(state=FSMAdminMasters.name)
async def load_name_m(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		async with state.proxy() as data:
			data['name'] = message.text
		await FSMAdminMasters.next()
		await message.reply("Введи стаж мастера :")

#Ловим третий ответ
#@dp.message_handler(state=FSMAdminMasters.exp)
async def load_exp_m(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		async with state.proxy() as data:
			data['exp'] = message.text
		await FSMAdminMasters.next()
		await message.reply("Введи место работы мастера :", reply_markup=admin_kb.button_case_adress)		
			
#Ловим четвертый (последний) ответ
#@dp.message_handler(state=FSMAdminMasters.location)
async def load_location_m(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		async with state.proxy() as data:
			data['location'] = message.text 
			await message.answer('Мастер добавлен !', reply_markup=admin_kb.button_case_admin)
	
	# База данныйх
	if data['location'] == 'пр. Ленина, 90':
		await sqlite_db.sql_add_commandlenina(state)
	
	elif data['location'] == 'Фрунзе 105':
		await sqlite_db.sql_add_commandfrynze(state)

	await state.finish()

#---------------------------------Машина состояний с инлайн кнопкой удалить мастера-------------------------

class FSMAdminDeleteMasters(StatesGroup):
	adres = State()
	delete = State()

# Код для управления ботом администратором
#@dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message:types.Message):
	global ID
	ID = message.from_user.id
	await bot.send_message(message.from_user.id, 'Что надо хозяин?', reply_markup=admin_kb.button_case_admin) # Другой способ добавления кнопки
	await message.delete()
	
# Начало диалога загрузки нового пункта меню
#@dp.message_handler(commands='Удалить_мастера', state=None)
async def cm_start_del(message: types.Message):
	if message.from_user.id == ID:
		await FSMAdminDeleteMasters.adres.set()
		await message.answer('Выбери адрес :', reply_markup=admin_kb.button_case_adress)

#Выход из состояний
#@dp.message_handler (state="*", commands= 'Отменить')
#@dp.message_handler (Text(equals='Отменить', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
	if message.from_user.id == ID: # Связь с адиминистратором
		current_state = await state.get_state()
		if current_state is None:
			return
		await state.finish()
		await message.reply('Отменил', reply_markup=admin_kb.button_case_admin)

#Ловим первый ответ от пользователя и пишем в словарь
#@dp.message_handler(state=FSMAdminDeleteMasters.adres)
async def adres_del(message: types.Message, state: FSMContext):
	if message.from_user.id == ID:
		async with state.proxy() as data:
			data['adres'] = message.text
		await FSMAdminDeleteMasters.next()
		await message.answer('Выбери мастера :', reply_markup=admin_kb.button_case_otmenit)

		if data['adres'] == 'пр. Ленина, 90':
			read = await sqlite_db.sql_readlenina()

		elif data['adres'] == 'Фрунзе 105':
			read = await sqlite_db.sql_readfrynze()

		for ret in read:
			
			await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\n{ret[2]}', reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Удалить {ret[1]}', callback_data=f'deletem {ret[1]}')))

#Ловим второй ответ
#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('deletem '), state=FSMAdminDeleteMasters.delete)
async def master_del(call: types.CallbackQuery, state: FSMContext):
	#if message.from_user.id == ID:
		async with state.proxy() as data:
			#data['delete'] = message.text
		
			if data['adres'] == 'пр. Ленина, 90':
				await sqlite_db.sql_delete_commandlenina(call.data.replace('deletem ', ''))
				
			elif data['adres'] == 'Фрунзе 105':
				await sqlite_db.sql_delete_commandfrynze(call.data.replace('deletem ', ''))
		
			await call.answer(text=f'{call.data.replace("deletem ", "")} удален.', show_alert=True)
			await call.message.answer(text=f'{call.data.replace("deletem ", "")} удален !', reply_markup=admin_kb.button_case_admin)
			#await bot.send_message(call.from_user.id, ret[0], f'{ret[1]}\n{ret[2]}', reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Удалить {ret[1]}', callback_data=f'deletem {ret[1]}')))
			await call.message.delete()
		
		await state.finish()

#-------------------------------------------Регистрация хендлеров--------------------------------------------

# Регистрируем хендлер и активируем его в главном коде
def register_handlers_admin(dp:Dispatcher):
	#----------------------------------Хендлеры добавить позицию---------------------------------------------
	dp.register_message_handler(cm_start, commands=['Загрузить'], state=None)
	dp.register_message_handler(cancel_handler, state="*", commands='Отменить')
	dp.register_message_handler(cancel_handler, Text(equals='Отменить', ignore_case=True), state="*")
	dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
	dp.register_message_handler(load_name, state=FSMAdmin.name)
	dp.register_message_handler(load_description, state=FSMAdmin.description)
	dp.register_message_handler(load_price, state=FSMAdmin.price)
	dp.register_message_handler(make_changes_command, commands=['moderator'], is_chat_admin=True)
	#----------------------------------Хендлеры удалить позицию----------------------------------------------
	dp.register_message_handler(delete_item, commands='Удалить')
	dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
	#----------------------------------Хендлеры добавить мастера---------------------------------------------
	dp.register_message_handler(cm_start_m, commands=['Загрузить_мастера'], state=None)
	dp.register_message_handler(load_photo_m, content_types=['photo'], state=FSMAdminMasters.photo)
	dp.register_message_handler(load_name_m, state=FSMAdminMasters.name)
	dp.register_message_handler(load_exp_m, state=FSMAdminMasters.exp)
	dp.register_message_handler(load_location_m, state=FSMAdminMasters.location)
	#----------------------------------Хендлеры удалить мастера----------------------------------------------
	dp.register_message_handler(cm_start_del, commands=['Удалить_мастера'], state=None)
	dp.register_message_handler(adres_del, state=FSMAdminDeleteMasters.adres)
	dp.register_callback_query_handler(master_del, lambda x: x.data and x.data.startswith('deletem '), state=FSMAdminDeleteMasters.delete)



