from aiogram.dispatcher import FSMContext # Машина состояний
from aiogram.dispatcher.filters.state import State, StatesGroup # Машина состояний
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db # База данных
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

#ID = None

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
		read = await sqlite_db.sql_read_promotion()
		for ret in read:
                                   
			await bot.send_photo(message.from_user.id, ret[2], f'**Название: {ret[1]}**\n{ret[3]}', reply_markup=admin_kb.get_admin_keyboard(ret[0]))
			
			#await bot.send_photo(message.from_user.id, promo_photo,)
			#await bot.send_message(message.from_user.id, f'Название: {promo_name}\n{promo_description}', reply_markup=get_admin_keyboard(promo_name))

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
				for ret in read:
					try:
						await bot.send_photo(ret[0], promotion[1], promotion[2])  # Отправка сообщения
					except Exception as e:	
						print(f"Не удалось отправить сообщение пользователю {ret[0]}: {e}")  # Ошибка, если пользователь заблокировал бота
						#sys.stderr.write(f"Не удалось отправить сообщение пользователю {ret[0]}: {e}\n")
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
		await sqlite_db.sql_del_command_promotion(promo_id)  # Выполняем удаление из базы данных
		await call.answer(f"Акция удалена !", show_alert=True)  # Уведомление пользователю
		await call.message.delete()  # Удаляем сообщение (если это нужно)

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

		await sqlite_db.sql_add_command_promotion(state)
		await bot.send_message(message.from_user.id, 'Акция добавлена!', reply_markup=admin_kb.button_case_newsletter)
		await state.finish()

#--------------------------------------------Регистрация хендлеров------------------------------------------
def register_handlers_admin(dp:Dispatcher):
	#dp.register_message_handler(make_changes_command, commands=['admin'], is_chat_admin=True)
	dp.register_message_handler(get_admins, commands=['admin'], is_chat_admin=True) 
	#dp.register_message_handler(get_admins, commands=['get_admins'])

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