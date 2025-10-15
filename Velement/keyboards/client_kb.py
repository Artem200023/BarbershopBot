from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove  #- что бы удалялась клава
from aiogram.types.web_app_info import WebAppInfo

button_auth = KeyboardButton('Авторизоваться', web_app=WebAppInfo(url='https://artem200023.github.io/MyProject/'))
b_auth = ReplyKeyboardMarkup(resize_keyboard=True).add(button_auth)

b_empty = ReplyKeyboardRemove()

#------------------------------------------------------------------------------------------
button_services = KeyboardButton('Наши услуги')
button_location = KeyboardButton('Расположение')
button_operating_mode = KeyboardButton('Режим работы')
button_company = KeyboardButton('О компании')
button_promo = KeyboardButton('Наши акции')
button_admin = KeyboardButton('Связаться с администратором')

button_case_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_services).add(button_admin).add(button_company)#.insert(button_operating_mode).add(button_admin)#.add(button_promo)

#------------------------------------------------------------------------------------------

button_otmena = KeyboardButton('Отмена')

kb_otmena = ReplyKeyboardMarkup(resize_keyboard=True).add(button_otmena)

#------------------------------------------------------------------------------------------
def get_client_chat():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("Перейти в чат", url="https://t.me/imtema2000"))
	return keyboard

def get_client_chat2(service_pid):
	keyboard = InlineKeyboardMarkup(row_width=1)
	keyboard.add(InlineKeyboardButton("Оставить заявку", url="https://t.me/imtema2000"))
	keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'services {service_pid}'))
	return keyboard

def get_location_services(service_pid):
	keyboard = InlineKeyboardMarkup(row_width=1)
	keyboard.add(InlineKeyboardButton(text='Иркутский проезд, 5 ст3', callback_data=f'locationI {service_pid}'))
	keyboard.add(InlineKeyboardButton(text='ул. Розы Люксембург, 133', callback_data=f'locationR {service_pid}'))
	keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'back_to_service {service_pid}'))
	return keyboard

