from aiogram.dispatcher import FSMContext # Машина состояний
from aiogram.dispatcher.filters.state import State, StatesGroup # Машина состояний
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db # База данных
from keyboards import admin_kb, client_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

admin_ids = []

# Код для управления ботом администратором
#@dp.message_handler(commands=['admin'], is_chat_admin=True)
async def get_admins(message: types.Message):
	global admin_ids
	chat_id = message.chat.id
	try:
		admins = await bot.get_chat_administrators(chat_id)
		admin_ids = [admin.user.id for admin in admins]
		await bot.send_message(message.from_user.id, 'Что надо хозяин ?', reply_markup=admin_kb.button_case_newsletter) # Другой способ добавления кнопки
		await message.delete()
        #await message.reply(f"ID администраторов: {', '.join(map(str, admin_ids))}")
        #await bot.send_message(message.from_user.id, f"ID администраторов: {', '.join(map(str, admin_ids))}")
	except Exception as e:
		await message.reply(f"Произошла ошибка: {e}")

#--------------------------------------------Подписчики-----------------------------------------------------------

# Подписчики
#@dp.message_handler(commands=['Подписчики'])
async def cm_subscribers(message:types.Message):
	if message.from_user.id in admin_ids:
		try:
			read = await sqlite_db.sql_read_name_clients()
			n = 0
			for ret in read:
				n += 1
			await bot.send_message(message.from_user.id, f"Подписчики : {n}", reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Список подписчиков', callback_data=f'subscribes')))
		except Exception as e:
			print(f"❌ Ошибка в cm_subscribers: {e}")
			await message.answer("Не удалось получить данные о подписчиках ⚠️")

#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('subscribes'))
async def send_subscribes(call: types.CallbackQuery):
	try:
		await call.answer()
		read = await sqlite_db.sql_read_name_clients()
		response_message = ""

		for ret in read:
			response_message += f"Имя : {ret[1]}\nТелефон : {ret[2]}\n\n"

		if response_message: 

			# Разбиваем сообщение на части по 4096 символов
			parts = [response_message[i:i + 4096] for i in range(0, len(response_message), 4096)]

			# Отправляем каждую часть отдельно
			for part in parts:
				await bot.send_message(call.message.chat.id, part)

		else:
			await bot.send_message(call.message.chat.id, "Нет подписчиков!")
	except Exception as e:
		print(f"❌ Ошибка в send_subscribes: {e}")

#----------------------------------------------Назад--------------------------------------------------------------

# Назад
#@dp.message_handler(commands=['Назад'])
async def cm_back(message:types.Message):
	if message.from_user.id in admin_ids:
		await bot.send_message(message.from_user.id, '...', reply_markup=admin_kb.button_case_newsletter) # Другой способ добавления кнопки

#--------------------------------------Пользовательское меню------------------------------------------------------

# Назад
#@dp.message_handler(commands=['Пользовательское_меню'])
async def cm_smenu(message:types.Message):
	if message.from_user.id in admin_ids:
		await bot.send_message(message.from_user.id, '...', reply_markup=client_kb.button_case_menu) # Другой способ добавления кнопки

#--------------------------------------------Акции----------------------------------------------------------------

# Меню акций
#@dp.message_handler(commands=['Акции'])
async def cm_promotion(message:types.Message):
	if message.from_user.id in admin_ids:
		await bot.send_message(message.from_user.id, '...', reply_markup=admin_kb.button_case_add_newsletter) # Другой способ добавления кнопки

#--------------------------------------------Мои акции с инлайн кнопками------------------------------------------

#@dp.message_handler(commands='Мои_акции')
async def cm_my_promotion(message: types.Message):
	if message.from_user.id in admin_ids:
		try:
			read = await sqlite_db.sql_read_promotion()
			if read:
				for ret in read:
                                   
					await bot.send_photo(message.from_user.id, ret[2], f'**Название: {ret[1]}**\n{ret[3]}', reply_markup=admin_kb.get_admin_keyboard(ret[0]))
			else:
				await message.answer("Акции еще не добавлены!")
		except Exception as e:
			print(f"❌ Ошибка в cm_my_promotion: {e}")		

#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('send '))
#@dp.callback_query_handler(lambda x: x.data and (x.data.startswith('send ') or x.data.startswith('confirSend ') or x.data.startswith('cancelSend ')))
async def send_promotions(call: types.CallbackQuery):
	#id_clients = {ret[0] for ret in read}
	#for client in id_clients:
	if call.data.startswith('send '):
		promo_id = call.data.replace('send ', '').strip()

		# Здесь мы используем edit_message_reply_markup для изменения клавиатуры
		await call.message.edit_reply_markup(reply_markup=admin_kb.get_admin_send(promo_id))

	elif call.data.startswith('confirmSend '):

		try:
        	# Получаем список клиентов
			read = await sqlite_db.sql_read_name_clients()
        
        	# Получаем информацию об акции
			promo_id = call.data.replace('confirmSend ', '').strip()  # Получаем название акции из колбэка
			promotion = await sqlite_db.sql_send_command_promotion(promo_id)

			# Здесь мы используем edit_message_reply_markup для изменения клавиатуры
			await call.message.edit_reply_markup(reply_markup=admin_kb.get_admin_keyboard(promo_id))
        
        	# Проверяем, нашли ли акцию
			if promotion:

            	# Отправляем сообщение каждому пользователю
				success_count = 0
				error_count = 0
				for ret in read:
					try:
						await bot.send_photo(ret[0], promotion[1], promotion[2])  # Отправка сообщения
						success_count += 1
						await asyncio.sleep(0.5)
					except Exception as e:
						error_count += 1     	
						#print(f"Не удалось отправить сообщение пользователю {ret[0]}: {e}")  # Ошибка, если пользователь заблокировал бота
				print(f"📊 Рассылка: {success_count} ✅ отправлено, {error_count} ❌ ошибок")
				await bot.answer_callback_query(call.id, f"Акция успешно отправлена !", show_alert=True)
			else:
				await bot.answer_callback_query(call.id, f"Акция не найдена !", show_alert=True)

		except Exception as e:	
			await bot.answer_callback_query(call.id, "Произошла ошибка при отправке акций !", show_alert=True)


	elif call.data.startswith('cancelSend '):
		promo_id = call.data.replace('cancelSend ', '').strip() #Получаем название акции из колбэка

		# Здесь мы используем edit_message_reply_markup для изменения клавиатуры
		await call.message.edit_reply_markup(reply_markup=admin_kb.get_admin_keyboard(promo_id))

		await call.answer("Рассылка акции отменена", show_alert=True)

#@dp.callback_query_handler(lambda x: x.data and (x.data.startswith('del ') or x.data.startswith('confirmRemove ') or x.data.startswith('cancelRemove ')))
async def remove_promotions(call: types.CallbackQuery):
	if call.data.startswith('del '):
		promo_id = call.data.replace('del ', '').strip()

		# Здесь мы используем edit_message_reply_markup для изменения клавиатуры
		await call.message.edit_reply_markup(admin_kb.get_admin_remove(promo_id))

	elif call.data.startswith('confirmRemove '):
		promo_id = call.data.replace('confirmRemove ', '').strip()  # Получаем название акции из колбэка
		try:
			await sqlite_db.sql_del_command_promotion(promo_id)  # Выполняем удаление из базы данных
			await call.answer(f"Акция удалена !", show_alert=True)  # Уведомление пользователю
			await call.message.delete()  # Удаляем сообщение (если это нужно)
		except Exception as e:
			print(f"❌ Ошибка удаления акции {promo_id}: {e}")
	elif call.data.startswith('cancelRemove '):
		promo_id = call.data.replace('cancelRemove ', '').strip() #Получаем название акции из колбэка

		# Здесь мы используем edit_message_reply_markup для изменения клавиатуры
		await call.message.edit_reply_markup(reply_markup=admin_kb.get_admin_keyboard(promo_id))
		await call.answer("Удаление акции отменено", show_alert=True)

#---------------------------------Машина состояний для добавления акций---------------------------------------------

class FSMAdminPromotion(StatesGroup):
	name = State()
	img = State()
	description = State()

# Код для управления ботом администратором
#@dp.message_handler(commands=['admin'])
async def get_admins(message: types.Message):
	global admin_ids
	chat_id = message.chat.id
	try:
		admins = await bot.get_chat_administrators(chat_id)
		admin_ids = [admin.user.id for admin in admins]
		await bot.send_message(message.from_user.id, 'Что надо хозяин ?', reply_markup=admin_kb.button_case_newsletter) # Другой способ добавления кнопки
		await message.delete()
        #await message.reply(f"ID администраторов: {', '.join(map(str, admin_ids))}")
        #await bot.send_message(message.from_user.id, f"ID администраторов: {', '.join(map(str, admin_ids))}")
	except Exception as e:
		await message.reply(f"Произошла ошибка: {e}")

# Начало диалога загрузки нового пункта меню
#@dp.message_handler(commands='Добавить_акцию', state=None)
async def cm_add_promotion(message: types.Message):
	if message.from_user.id in admin_ids:
		await FSMAdminPromotion.name.set()
		await message.reply('Введи название акции', reply_markup=admin_kb.button_case_cancel)

#Ловим 1-ый ответ от пользователя и пишем в словарь
#@dp.message_handler(state=FSMAdminPromotion.name)
async def load_name_promotion(message: types.Message, state: FSMContext):
	if message.from_user.id in admin_ids: # Связь с адиминистратором
		async with state.proxy() as data:
			data['name'] = message.text
		await FSMAdminPromotion.next()
		await message.reply('Загрузи фото', reply_markup=admin_kb.button_case_cancel)

#Выход из состояний
#@dp.message_handler (state="*", commands= 'Отменить')
#@dp.message_handler (Text(equals='Отменить', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
	if message.from_user.id in admin_ids: # Связь с адиминистратором
		current_state = await state.get_state()
		if current_state is None:
			return
		await state.finish()
		await message.reply('Отменил', reply_markup=admin_kb.button_case_newsletter)

#Ловим 2-ой ответ от пользователя и пишем в словарь
#@dp.message_handler(content_types=['photo'], state=FSMAdminPromotion.img)
async def load_img_promotion(message: types.Message, state: FSMContext):
	if message.from_user.id in admin_ids: # Связь с адиминистратором
		async with state.proxy() as data:
			data['img'] = message.photo[0].file_id
		await FSMAdminPromotion.next()
		await message.reply("Введи описание акции")

#Ловим 3-ий ответ 
#@dp.message_handler(state=FSMAdminPromotion.description)
async def load_description_promotion(message: types.Message, state: FSMContext):
	if message.from_user.id in admin_ids:  # Связь с адиминистратором
		async with state.proxy() as data:
			data['description'] = message.text
			total_length = len(data['name']) + len(data['description'])
			diff = total_length - 1000
			# Проверка на превышение лимита символов
			if total_length > 1000: # 1011 символов максимально
				await message.reply(
					f"Ограничение символов в телеграмме, убери {diff} символа"
				)
				return  # Завершаем выполнение функции, чтобы пользователь мог исправить описание
		try:
			await sqlite_db.sql_add_command_promotion(state)
			await bot.send_message(message.from_user.id, 'Акция добавлена!', reply_markup=admin_kb.button_case_newsletter)
		except Exception as e:
			print(f"❌ Ошибка добавления акции: {e}")
		
		await state.finish()

#--------------------------------------------Услуги----------------------------------------------------------------

# Меню акций
#@dp.message_handler(commands=['Услуги'])
async def cm_services(message:types.Message):
	if message.from_user.id in admin_ids:
		await bot.send_message(message.from_user.id, '...', reply_markup=admin_kb.button_case_add_services) # Другой способ добавления кнопки

#--------------------------------------------Мои услуги с инлайн кнопками------------------------------------------

#@dp.message_handler(commands='Мои_услуги')
async def cm_my_services(message: types.Message):
	if message.from_user.id in admin_ids:
		try:
			read = await sqlite_db.sql_read_services()
			if read:
				for ret in read:
					await bot.send_photo(message.from_user.id, ret[2], f'{ret[1]}', reply_markup=admin_kb.get_admin_keyboard_services(ret[0]))
			else:
				await message.answer("Услуги еще не добавлены!")
		except Exception as e:
			print(f"❌ Ошибка в cm_my_services: {e}")

#@dp.callback_query_handler(lambda x: x.data and (x.data.startswith('del ') or x.data.startswith('confirmRemove ') or x.data.startswith('cancelRemove ')))
async def remove_services(call: types.CallbackQuery):
	if call.data.startswith('delServices '):
		services_id = call.data.replace('delServices ', '').strip()

		# Здесь мы используем edit_message_reply_markup для изменения клавиатуры
		await call.message.edit_reply_markup(admin_kb.get_admin_remove_services(services_id))

	elif call.data.startswith('confirmRemoveServices '):
		services_id = call.data.replace('confirmRemoveServices ', '').strip()  # Получаем название акции из колбэка
		try:	
			await sqlite_db.sql_del_command_services(services_id)  # Выполняем удаление из базы данных
			await call.answer(f"Услуга удалена !", show_alert=True)  # Уведомление пользователю
			await call.message.delete()  # Удаляем сообщение (если это нужно)
		except Exception as e:
			print(f"❌ Ошибка удаления услуги {services_id}: {e}")
	
	elif call.data.startswith('cancelRemoveServices '):
		services_id = call.data.replace('cancelRemoveServices ', '').strip() #Получаем название акции из колбэка

		# Здесь мы используем edit_message_reply_markup для изменения клавиатуры
		await call.message.edit_reply_markup(reply_markup=admin_kb.get_admin_keyboard_services(services_id))
		await call.answer("Удаление услуги отменено", show_alert=True)


#---------------------------------Машина состояний для добавления услуг---------------------------------------------

class FSMAdminServices(StatesGroup):
	name = State()
	img = State()

# Код для управления ботом администратором
#@dp.message_handler(commands=['admin'])
async def get_admins(message: types.Message):
	global admin_ids
	chat_id = message.chat.id
	try:
		admins = await bot.get_chat_administrators(chat_id)
		admin_ids = [admin.user.id for admin in admins]
		await bot.send_message(message.from_user.id, 'Что надо хозяин ?', reply_markup=admin_kb.button_case_newsletter) # Другой способ добавления кнопки
		await message.delete()
        #await message.reply(f"ID администраторов: {', '.join(map(str, admin_ids))}")
        #await bot.send_message(message.from_user.id, f"ID администраторов: {', '.join(map(str, admin_ids))}")
	except Exception as e:
		await message.reply(f"Произошла ошибка: {e}")

# Начало диалога загрузки нового пункта меню
#@dp.message_handler(commands='Добавить_услугу', state=None)
async def cm_add_services(message: types.Message):
	if message.from_user.id in admin_ids:
		await FSMAdminServices.name.set()
		await message.reply('Введи название услуги', reply_markup=admin_kb.button_case_cancel)

#Ловим 1-ый ответ от пользователя и пишем в словарь
#@dp.message_handler(state=FSMAdminServices.name)
async def load_name_services(message: types.Message, state: FSMContext):
	if message.from_user.id in admin_ids: # Связь с адиминистратором
		async with state.proxy() as data:
			data['name'] = message.text
		await FSMAdminServices.next()
		await message.reply('Загрузи фото', reply_markup=admin_kb.button_case_cancel)

#Выход из состояний
#@dp.message_handler (state="*", commands= 'Отменить')
#@dp.message_handler (Text(equals='Отменить', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
	if message.from_user.id in admin_ids: # Связь с адиминистратором
		current_state = await state.get_state()
		if current_state is None:
			return
		await state.finish()
		await message.reply('Отменил', reply_markup=admin_kb.button_case_newsletter)

#Ловим 2-ой ответ от пользователя и пишем в словарь
#@dp.message_handler(content_types=['photo'], state=FSMAdminServices.img)
async def load_img_services(message: types.Message, state: FSMContext):
	if message.from_user.id in admin_ids: # Связь с адиминистратором
		try:
			async with state.proxy() as data:
				data['img'] = message.photo[0].file_id
			await sqlite_db.sql_add_command_services(state)
			await bot.send_message(message.from_user.id, 'Услуга добавлена!', reply_markup=admin_kb.button_case_newsletter)
		except Exception as e:
			print(f"❌ Ошибка добавления услуги: {e}")

		await state.finish()

#--------------------------------------------Регистрация хендлеров------------------------------------------
def register_handlers_admin(dp:Dispatcher):

#----------------------------------Кнопки клавиатуры админа---------------------------------
	dp.register_message_handler(get_admins, commands=['admin'], is_chat_admin=True)

	dp.register_message_handler(cm_subscribers, commands=['Подписчики'])
	dp.register_callback_query_handler(send_subscribes, lambda x: x.data and x.data.startswith('subscribes'))
	dp.register_message_handler(cm_smenu, commands=['Пользовательское_меню'])
	dp.register_message_handler(cm_back, commands=['Назад'])

#--------------------------------------------Акции------------------------------------------
	dp.register_message_handler(cm_promotion, commands=['Акции'])
	dp.register_message_handler(cm_my_promotion, commands=['Мои_акции'])

	dp.register_callback_query_handler(send_promotions, lambda x: x.data and (x.data.startswith('send ') or x.data.startswith('confirmSend ') or x.data.startswith('cancelSend ')))
	dp.register_callback_query_handler(remove_promotions, lambda x: x.data and (x.data.startswith('del ') or x.data.startswith('confirmRemove ') or x.data.startswith('cancelRemove ')))                                   
	dp.register_message_handler(cancel_handler, state="*", commands='Отменить')
	dp.register_message_handler(cancel_handler, Text(equals='Отменить', ignore_case=True), state="*")


#------------------------------------------Машина состояний добавить акцию-----------------------------------------------------------
	dp.register_message_handler(cm_add_promotion, commands='Добавить_акцию', state=None)
	dp.register_message_handler(load_name_promotion, state=FSMAdminPromotion.name)
	dp.register_message_handler(load_img_promotion, content_types=['photo'], state=FSMAdminPromotion.img)
	dp.register_message_handler(load_description_promotion, state=FSMAdminPromotion.description)

#--------------------------------------------Услуги------------------------------------------
	dp.register_message_handler(cm_services, commands=['Услуги'])
	dp.register_message_handler(cm_my_services, commands=['Мои_услуги'])

	#dp.register_callback_query_handler(send_services, lambda x: x.data and (x.data.startswith('send ') or x.data.startswith('confirmSend ') or x.data.startswith('cancelSend ')))
	dp.register_callback_query_handler(remove_services, lambda x: x.data and (x.data.startswith('delServices ') or x.data.startswith('confirmRemoveServices ') or x.data.startswith('cancelRemoveServices ')))                                   

#------------------------------------------Машина состояний добавить услугу-----------------------------------------------------------
	dp.register_message_handler(cm_add_services, commands='Добавить_услугу', state=None)
	dp.register_message_handler(load_name_services, state=FSMAdminServices.name)
	dp.register_message_handler(load_img_services, content_types=['photo'], state=FSMAdminServices.img)
