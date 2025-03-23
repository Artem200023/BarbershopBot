from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove  #- что бы удалялась клава


button_phone = KeyboardButton('Авторизоваться', request_contact=True)
b_phone = ReplyKeyboardMarkup(resize_keyboard=True).add(button_phone)

b_empty = ReplyKeyboardRemove()

button_promo = KeyboardButton('Наши акции')
button_admin = KeyboardButton('Связаться с администратором')

button_case_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_promo).add(button_admin)

def get_client_chat():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("Перейти в чат", url="https://t.me/imtema2000"))
	return keyboard
