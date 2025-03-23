#from aiogram.dispatcher import FSMContext # Для того что бы работала последовательность (машина состояний)
#from aiogram.dispatcher.filters.state import State, StatesGroup # Машина состояний
#from keyboards.client_kb import kb_phone # Это с __init__.py
from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import client_kb
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from data_base import sqlite_db
from data import data_db
from aiogram.dispatcher.filters import Text

import json # Пробник

#@dp.message_handler(commands=['start', 'help'])
# По вызову команд будут определенные сообщения
async def command_start(message:types.Message):

	#await bot.send_message(message.from_user.id, 'Хорошего настроения !')            
	#await bot.send_message(message.from_user.id, 'Хорошего настроения !', reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Оставить чаевые', callback_data=f'tips')))
	await bot.send_message(
	message.from_user.id,
	'''Привет! 👋 Добро пожаловать в барбершоп КИРОВ! 

Мы рады видеть вас в нашем боте! Здесь вы можете легко управлять своими записями и получать актуальную информацию о наших услугах. ✂️

Что вы можете сделать :
📍 Авторизация : Авторизируйтесь, чтобы получить доступ к персонализированным услугам.
📍 Наши акции : Узнайте о наших текущих акциях и специальных предложениях, чтобы не упустить возможность сэкономить!
📍 Связь с администратором : У вас есть вопросы или пожелания? Напишите нам, и мы с радостью ответим!
📍 Онлайн-запись : В нашем Telegram-боте интегрировано мини-приложение, с помощью которого вы можете записаться на стрижку прямо здесь!

Спасибо, что выбрали нас! Мы готовы сделать ваш образ стильным и уникальным! 💈''',
	reply_markup=client_kb.b_phone
)
	await message.delete()

#----------------------------------------------------------------------------------------------------------------
#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('tips'))
async def tips(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id) # Что бы не было мигания после нажатия на инлайн кнопку
    #await bot.send_message(callback_query.from_user.id, "Привет")
    await call.message.answer("Привет")
#----------------------------------------------------------------------------------------------------------------

#@dp.message_handler(content_types=[types.ContentType.CONTACT])
async def log_in(message: types.Message):
		user_id = message.from_user.id
		username = message.from_user.username
		phone = message.contact.phone_number

		if await sqlite_db.is_phone_subscribed_clients(phone):
			await message.answer("Вы уже авторизованы !", reply_markup=client_kb.button_case_menu) 
		else:
			await sqlite_db.sql_add_command_clients(user_id, username, phone)
			await message.answer("Вы успешно авторизованы !", reply_markup=client_kb.button_case_menu)

#@dp.message_handler(lambda message:'Наши акции' in message.text)            
# По вызову команд будут определенные сообщения
async def c_promo(message:types.Message):                                         
		read = await sqlite_db.sql_read_promotion()
		for ret in read:

			await bot.send_photo(message.from_user.id, ret[2], f'\n{ret[3]}')
			
#@dp.message_handler(lambda message:'Связаться с администратором' in message.text)            
async def c_admin(message:types.Message):                                         
	await message.answer("Нажмите на кнопку ниже, чтобы перейти в чат:", reply_markup=client_kb.get_client_chat())
	
#----------------------------------------------------------------------------------------------------------------
			
#-----------------------------------------------------------------------------------------------------------
#После того как пользователь записался в форме записи yclients отправить уведомление о записи в телеграм
#-----------------------------------------------------------------------------------------------------------

def register_handlers_client(dp:Dispatcher):
	dp.register_message_handler(command_start, commands=['start', 'help'])
	dp.register_callback_query_handler(tips, lambda x: x.data and x.data.startswith('tips'))
	dp.register_message_handler(log_in, content_types=[types.ContentType.CONTACT])

	dp.register_message_handler(c_promo, lambda message:'Наши акции' in message.text)
	dp.register_message_handler(c_admin, lambda message:'Связаться с администратором' in message.text)

