from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


#--------------------------Кнопка отменить------------------------------------------

button_cancel = KeyboardButton('Отменить')

button_case_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)

#--------------------------Кнопки клавиатуры админа---------------------------------
button_newsletter = KeyboardButton('/Акции')
button_services = KeyboardButton('/Услуги')
button_subscribers = KeyboardButton('/Подписчики')
button_smenu = KeyboardButton('/Пользовательское_меню')

button_case_newsletter = ReplyKeyboardMarkup(resize_keyboard=True).add(button_newsletter).add(button_services).add(button_subscribers).add(button_smenu)


#--------------------------Кнопка акциии--------------------------------------------
button_my_newsletter = KeyboardButton('/Мои_акции')
button_add_newsletter = KeyboardButton('/Добавить_акцию')
button_back = KeyboardButton('/Назад')

button_case_add_newsletter = ReplyKeyboardMarkup(resize_keyboard=True).add(button_my_newsletter).add(button_add_newsletter).add(button_back)

#--------------------------Кнопка услуги--------------------------------------------
button_my_services = KeyboardButton('/Мои_услуги')
button_add_services = KeyboardButton('/Добавить_услугу')
button_back = KeyboardButton('/Назад')

button_case_add_services = ReplyKeyboardMarkup(resize_keyboard=True).add(button_my_services).add(button_add_services).add(button_back)


#--------------------------Инлайн кнопки акции------------------------------------------

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

#--------------------------Инлайн кнопки услуги------------------------------------------

def get_admin_keyboard_services(services_id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton(f'Удалить', callback_data=f'delServices {services_id}'))
	return keyboard

def get_admin_remove_services(services_id):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton(f'Подтвердить', callback_data=f'confirmRemoveServices {services_id}'))
	keyboard.add(InlineKeyboardButton(f'Отменить', callback_data=f'cancelRemoveServices {services_id}'))
	return keyboard