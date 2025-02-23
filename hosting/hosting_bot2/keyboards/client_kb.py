# Добавляем классы
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove #- что бы удалялась клава

# То что будет отображаться на кнопке
b1 = KeyboardButton("Режим работы")
b2 = KeyboardButton("Расположение")
b3 = KeyboardButton("Меню")
b4 = KeyboardButton("Записаться на стрижку")
#b4 = KeyboardButton('Поделиться номером', request_contact=True) # request_contact=True - номер телефона
#b5 = KeyboardButton('Отправить где я', request_location=True) # request_location=True - геолокация

# Создаем переменную и запускаем класс, замена обычной клавиатуры на нашу
# resize_keyboard=True - Уменьшить кнопки, one_time_keyboard=True - при нажатии кнопки уходят
kb_client = ReplyKeyboardMarkup(resize_keyboard=True) #, one_time_keyboard=True)

# add - добавит кнопки с новой строки, insert - добавит кнопки с боку, row - добавит кнопки в строчку
kb_client.add(b1).add(b2).insert(b3).add(b4)

#_________________________________________________________________________________________

button_phone = KeyboardButton('Поделиться номером', request_contact=True)
button_otmena1 = KeyboardButton('Отмена')

kb_phone = ReplyKeyboardMarkup(resize_keyboard=True).add(button_phone).add(button_otmena1)

#__________________________________________________________________________________________

button_otmena = KeyboardButton('Отмена')

kb_otmena = ReplyKeyboardMarkup(resize_keyboard=True).add(button_otmena)

#__________________________________________________________________________________________