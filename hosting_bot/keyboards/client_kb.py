# Добавляем классы
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove  #- что бы удалялась клава

#------------------------------------------------------------------------------------------
# То что будет отображаться на кнопке
b1 = KeyboardButton("Режим работы")
b2 = KeyboardButton("Расположение")
b3 = KeyboardButton("Меню")
b4 = KeyboardButton("Записаться на стрижку")
#button_phone = types.KeyboardButton(text="Подписаться", request_contact=True)
#b4 = KeyboardButton('Поделиться номером', request_contact=True) # request_contact=True - номер телефона
#b5 = KeyboardButton('Отправить где я', request_location=True) # request_location=True - геолокация

# Создаем переменную и запускаем класс, замена обычной клавиатуры на нашу
# resize_keyboard=True - Уменьшить кнопки, one_time_keyboard=True - при нажатии кнопки уходят
kb_client = ReplyKeyboardMarkup(resize_keyboard=True) #, one_time_keyboard=True)

# add - добавит кнопки с новой строки, insert - добавит кнопки с боку, row - добавит кнопки в строчку
kb_client.add(b1).add(b2).insert(b3).add(b4)

#------------------------------------------------------------------------------------------
# То что будет отображаться на кнопке
b1 = KeyboardButton("Режим работы")
b2 = KeyboardButton("Расположение")
b3 = KeyboardButton("Меню")
b4 = KeyboardButton("Записаться на стрижку")
b5 = KeyboardButton("Подписаться", request_contact=True)
#button_phone = types.KeyboardButton(text="Подписаться", request_contact=True)
#b4 = KeyboardButton('Поделиться номером', request_contact=True) # request_contact=True - номер телефона
#b5 = KeyboardButton('Отправить где я', request_location=True) # request_location=True - геолокация

# Создаем переменную и запускаем класс, замена обычной клавиатуры на нашу
# resize_keyboard=True - Уменьшить кнопки, one_time_keyboard=True - при нажатии кнопки уходят
kb_client2 = ReplyKeyboardMarkup(resize_keyboard=True) #, one_time_keyboard=True)

# add - добавит кнопки с новой строки, insert - добавит кнопки с боку, row - добавит кнопки в строчку
kb_client2.add(b1).add(b2).insert(b3).add(b4).add(b5)

#------------------------------------------------------------------------------------------

button_phone = KeyboardButton('Поделиться номером', request_contact=True)
button_otmena1 = KeyboardButton('Отмена')

kb_phone = ReplyKeyboardMarkup(resize_keyboard=True).add(button_phone).add(button_otmena1)

#------------------------------------------------------------------------------------------

button_otmena = KeyboardButton('Отмена')

kb_otmena = ReplyKeyboardMarkup(resize_keyboard=True).add(button_otmena)

#------------------------------------------------------------------------------------------

button_lenina = KeyboardButton('пр. Ленина, 90')
button_frynze = KeyboardButton('Фрунзе 105')

kb_case_adres = ReplyKeyboardMarkup(resize_keyboard=True).add(button_lenina).add(button_frynze).add(button_otmena)

#---------------------------------------Инлайн кнопка выбрать------------------------------

# По идее работает не будет только имени кого выбирать просто "Выбрать"

#b8 = InlineKeyboardButton(text=f'Выбрать {ret[1]}', callback_data='www')

#kb_case_inline = InlineKeyboardMarkup(row_width=1).add(b8)  

#InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Выбрать {ret[1]}', callback_data='www'))  