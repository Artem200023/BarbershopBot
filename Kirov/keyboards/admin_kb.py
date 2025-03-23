from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


#--------------------------Кнопка отменить------------------------------------------

button_cancel = KeyboardButton('Отменить')

button_case_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)

#--------------------------Кнопки клавиатуры админа---------------------------------
button_my_newsletter = KeyboardButton('/Мои_акции')
button_add_newsletter = KeyboardButton('/Добавить_акцию')

button_case_add_newsletter = ReplyKeyboardMarkup(resize_keyboard=True).add(button_my_newsletter).add(button_add_newsletter)

#--------------------------Кнопка акциии--------------------------------------------
button_newsletter = KeyboardButton('/Акции')

button_case_newsletter = ReplyKeyboardMarkup(resize_keyboard=True).add(button_newsletter)


#--------------------------Инлайн кнопки------------------------------------------

def get_admin_keyboard(promo_id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton(f'Рассылка', callback_data=f'send {promo_id}'))
	keyboard.add(InlineKeyboardButton(f'Удалить', callback_data=f'del {promo_id}'))
	return keyboard

def get_admin_send(promo_id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton(f'Подтвердить', callback_data=f'confirmSend {promo_id}'))
	keyboard.add(InlineKeyboardButton(f'Отменить', callback_data=f'cancelSend {promo_id}'))
	return keyboard

def get_admin_remove(promo_id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton(f'Подтвердить', callback_data=f'confirmRemove {promo_id}'))
	keyboard.add(InlineKeyboardButton(f'Отменить', callback_data=f'cancelRemove {promo_id}'))
	return keyboard