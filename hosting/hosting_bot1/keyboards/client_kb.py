# Добавляем классы
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton#, ReplyKeyboardRemove - что бы удалялась клава

# То что будет отображаться на кнопке
b1 = KeyboardButton("Режим работы")
b2 = KeyboardButton("Расположение")
b3 = KeyboardButton("Меню")
#b4 = KeyboardButton('Поделиться номером', request_contact=True) # request_contact=True - номер телефона
#b5 = KeyboardButton('Отправить где я', request_location=True) # request_location=True - геолокация

# Создаем переменную и запускаем класс, замена обычной клавиатуры на нашу
# resize_keyboard=True - Уменьшить кнопки, one_time_keyboard=True - при нажатии кнопки уходят
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)#, one_time_keyboard=True)

# add - добавит кнопки с новой строки, insert - добавит кнопки с боку, row - добавит кнопки в строчку
kb_client.add(b1).add(b2).insert(b3)#.row(b4, b5)