from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


#--------------------------Кнопка отменить------------------------------------------

button_otmenit = KeyboardButton('Отменить')

button_case_otmenit = ReplyKeyboardMarkup(resize_keyboard=True).add(button_otmenit)

#--------------------------Кнопки клавиатуры админа---------------------------------
button_load = KeyboardButton('/Загрузить')
button_delete = KeyboardButton('/Удалить')
button_load_m = KeyboardButton('/Загрузить_мастера')
button_delete_m = KeyboardButton('/Удалить_мастера')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load)\
			.add(button_delete).add(button_load_m).add(button_delete_m)

#--------------------------Кнопки адресов------------------------------------------

button_lenina = KeyboardButton('пр. Ленина, 90')
button_frynze = KeyboardButton('Фрунзе 105')

button_case_adress = ReplyKeyboardMarkup(resize_keyboard=True).add(button_lenina).add(button_frynze).add(button_otmenit)
#button_adress = ReplyKeyboardMarkup(resize_keyboard=True).add(button_lenina).add(button_frynze)

#--------------------------Инлайн кнопки------------------------------------------

#b1 = InlineKeyboardButton(f'Удалить {ret[1]}')

#button_case_adress = ReplyKeyboardMarkup(resize_keyboard=True).add(button_lenina).add(button_frynze).add(button_otmenit)



#reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}'))