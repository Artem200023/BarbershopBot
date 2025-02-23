from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



#--------------------------Кнопки клавиатуры админа---------------------------------
button_load = KeyboardButton('/Загрузить')
button_delete = KeyboardButton('/Удалить')


button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load)\
			.add(button_delete)
#--------------------------Кнопка отменить------------------------------------------

button_otmenit = KeyboardButton('Отменить')

button_case_otmenit = ReplyKeyboardMarkup(resize_keyboard=True).add(button_otmenit)

#-----------------------------------------------------------------------------------