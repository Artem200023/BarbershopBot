from aiogram import types, Dispatcher
from create_bot import dp

import json, string

#@dp.message_handler()
async def echo_send(message : types.Message):
	if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')}\
		.intersection(set(json.load(open('cenz.json')))) != set():
		await message.reply('Маты запрещены !')
		await message.delete()

	elif message.text == 'Привет':
		await message.answer('И тебе привет !')

	elif message.text == 'Салам':
		await message.answer('И тебе салам !')

	elif message.text == 'Здарова':
		await message.answer('И тебе здарова !')
		
	#else:
		
		#await message.answer('Проще общайся !')
	
# Регистрируем хендлер и активируем его в главном коде
def register_handlers_other(dp:Dispatcher):
	dp.register_message_handler(echo_send)