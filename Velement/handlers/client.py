from aiogram.dispatcher import FSMContext # Для того что бы работала последовательность (машина состояний)
from aiogram.dispatcher.filters.state import State, StatesGroup # Машина состояний
#from keyboards.client_kb import kb_phone # Это с __init__.py
from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import client_kb
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from data_base import sqlite_db
from data import data_db
from aiogram.dispatcher.filters import Text
from aiogram_calendar_rus import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar
from scheduler.scheduler_options import BirthdayService

from aiogram.types.web_app_info import WebAppInfo

import json # Пробник

#def get_client_location_services(services_id):
	#keyboard = InlineKeyboardMarkup()
	#keyboard.add(InlineKeyboardButton(f'Подтвердить', callback_data=f'confirmRemoveServices {services_id}'))
	#keyboard.add(InlineKeyboardButton(f'Отменить', callback_data=f'cancelRemoveServices {services_id}'))
	#return keyboard

#@dp.message_handler(commands=['start', 'help'])
# По вызову команд будут определенные сообщения
async def command_start(message:types.Message):

	#await bot.send_message(message.from_user.id, 'Хорошего настроения !')            
	#await bot.send_message(message.from_user.id, 'Хорошего настроения !', reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Оставить чаевые', callback_data=f'tips')))
	await bot.send_message(
	message.from_user.id,
	'''Привет! 👋 Добро пожаловать в автосервис "Вмятый элемент" ! 

Мы рады видеть вас в нашем боте! Здесь вы можете легко выбирать услугу и получать актуальную информацию о наших услугах. 

Что вы можете сделать :
📍 Авторизация : Авторизируйтесь, чтобы получить доступ к персонализированным услугам.
📍 Наши акции : Узнайте о наших текущих акциях и специальных предложениях, чтобы не упустить возможность сэкономить!
📍 Связь с администратором : У вас есть вопросы или пожелания? Напишите нам, и мы с радостью ответим!''',
	reply_markup=client_kb.b_auth
)
	await message.delete()

#----------------------------------------------------------------------------------------------------------------

#@dp.message_handler(content_types=['web_app_data']) 
async def web_authorization(message: types.Message):
    """Обработка данных из Mini App формы"""
    
    print(f"=== ПОЛУЧЕНЫ ДАННЫЕ ИЗ WEB APP ===")
    print(f"User ID: {message.from_user.id}")
    print(f"WebApp data: {message.web_app_data}")
    
    try:
        # Получаем данные из веб-приложения
        web_app_data = message.web_app_data
        data_json = web_app_data.data
        
        print(f"Raw JSON data: {data_json}")
        
        # Парсим JSON
        form_data = json.loads(data_json)
        
        print(f"Parsed form data: {form_data}")
        
        # Извлекаем данные из формы
        last_name = form_data.get('lastName', '')
        first_name = form_data.get('firstName', '')
        middle_name = form_data.get('middleName', '')
        phone = form_data.get('phone', '')
        birth_date = form_data.get('birthDate', '')
        telegram_id = form_data.get('telegramId') or message.from_user.id
        
        print(f"Extracted data - Name: {last_name} {first_name}, Phone: {phone}, Birth: {birth_date}")
        
        # Проверяем обязательные поля
        if not all([last_name, first_name, phone, birth_date]):
            await message.answer("❌ Не все обязательные поля заполнены")
            return
        
        # Формируем полное имя
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        
        # Проверяем, есть ли пользователь уже в базе
        if await sqlite_db.is_user_subscribed_clients(telegram_id):
            await message.answer("Вы уже авторизованы! ✅", reply_markup=client_kb.button_case_menu)
        else:
            # Сохраняем пользователя
            user_data = {
                'user_id': telegram_id,
                'username': full_name,
                'phone': phone,
                'birth_date': birth_date
            }
            
            # Используем существующую функцию для сохранения
            await sqlite_db.sql_add_command_clients(user_data)
            
            await message.answer("Вы успешно авторизованы! ✅", reply_markup=client_kb.button_case_menu)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        await message.answer("❌ Ошибка при обработке данных формы. Попробуйте еще раз.")
    except Exception as e:
        print(f"General error: {e}")
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

#--------------------------------------------Наши акции------------------------------------------------------------

#@dp.message_handler(lambda message:'Наши акции' in message.text)            
# По вызову команд будут определенные сообщения
async def c_promo(message:types.Message):  
    try:
        read = await sqlite_db.sql_read_promotion()
        if read:  
            for ret in read:
                try:
                    await bot.send_photo(message.from_user.id, ret[2], f'\n{ret[3]}')
                except Exception as e:
                    print(f"❌ Ошибка отправки акций: {e}")
        else:
            await message.answer("Акции временно отсутствуют 📭")
    
    except Exception as e:
        print(f"❌ Ошибка загрузки акций: {e}")

#@dp.message_handler(lambda message:'Связаться с администратором' in message.text)            
async def c_admin(message:types.Message):                            
    await message.answer("Нажмите на кнопку ниже, чтобы перейти в чат:", reply_markup=client_kb.get_client_chat())

#@dp.message_handler(lambda message:'О компании' in message.text)            
async def c_company(message:types.Message):  
    await message.answer("""
🏢 *О КОМПАНИИ*

📍 *Адрес:*
                      
ул. Розы Люксембург, 133           
Иркутский проезд, 5 ст3

🕒 *Режим работы:*
                      
• Понедельник-Пятница: 9:00 - 18:00
• Суббота: 10:00 - 16:00
• Воскресенье: выходной
        """)

#await bot.send_photo(message.from_user.id, ret[2], reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'{ret[1]}', callback_data=f'services {ret[0]}')))
#--------------------------------------------Наши услуги------------------------------------------------------------

#@dp.message_handler(lambda message:'Наши услуги' in message.text)            
async def c_services(message:types.Message):   
    try:
        await bot.send_message(message.from_user.id, "Выберете услугу:")                                      
        read = await sqlite_db.sql_read_services()

        if read:
            for ret in read:
                try:
                    # ret[0] - pid, ret[1] - name, ret[2] - img
                    await bot.send_photo(message.from_user.id, ret[2], reply_markup=InlineKeyboardMarkup(row_width=1)
								 .add(InlineKeyboardButton(text=f'{ret[1]}', callback_data=f'services {ret[0]}')))
                except Exception as e:
                    print(f"❌ Ошибка отправки услуги: {e}")

        else:
            await message.answer("Услуги временно отсутствуют 📭")
    except Exception as e:
        print(f"❌ Ошибка загрузки услуг: {e}")

#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('services '))
async def location_services(call: types.CallbackQuery):
    try:
        if call.data.startswith('services '):
            # Разделяем на пробелы и вытаскиваем значение из callback после проела (там название)
            service_pid = call.data.split(' ')[1]
        
            await call.message.edit_reply_markup(reply_markup=client_kb.get_location_services(service_pid))
    except Exception as e:
        print(f"❌ Ошибка в location_services: {e}")

#@dp.callback_query_handler(lambda x: x.data and (x.data.startswith('locationI ') or x.data.startswith('locationR ') or x.data.startswith('back_to_service ')))
async def chat_services(call: types.CallbackQuery):
    try:
        if call.data.startswith('locationI '):
            service_pid = call.data.split(' ')[1]
            await call.message.edit_reply_markup(reply_markup=client_kb.get_client_chat2(service_pid))

        
        elif call.data.startswith('locationR '):
            service_pid = call.data.split(' ')[1]
            await call.message.edit_reply_markup(reply_markup=client_kb.get_client_chat2(service_pid))
        
        elif call.data.startswith('back_to_service '):
            # Возвращаемся к адресам
            service_pid = call.data.split(' ')[1]
        
            # Получаем данные услуги из БД по pid
            service_data = await sqlite_db.sql_send_command_services(service_pid)
            if service_data:
                service_name = service_data[0]  # name из БД
            
                # Восстанавливаем оригинальную кнопку с той же услугой
                await call.message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup(row_width=1).add(
                        InlineKeyboardButton(text=service_name, callback_data=f'services {service_pid}')
                    )
                )
    except Exception as e:
        print(f"❌ Ошибка в chat_services: {e}")
#-----------------------------------------------------------------------------------------------------------
#После того как пользователь записался в форме записи yclients отправить уведомление о записи в телеграм
#-----------------------------------------------------------------------------------------------------------

#@dp.message_handler(commands=['test_scheduler'])
async def test_scheduler_command(message: types.Message):
    """Тест планировщика вручную"""
    from scheduler.scheduler_options import BirthdayService
    service = BirthdayService(bot, dp)
    await service.daily_birthday_check()
    await message.answer("✅ Тестовая проверка выполнена!")

def register_handlers_client(dp:Dispatcher):
	dp.register_message_handler(command_start, commands=['start', 'help'])
	dp.register_message_handler(web_authorization, content_types=['web_app_data']) 


	dp.register_message_handler(c_promo, lambda message:'Наши акции' in message.text)
	dp.register_message_handler(c_services, lambda message:'Наши услуги' in message.text)
	
	dp.register_callback_query_handler(location_services, lambda x: x.data and x.data.startswith('services '))
	dp.register_callback_query_handler(chat_services, lambda x: x.data and (x.data.startswith('locationI ') or x.data.startswith('locationR ') or x.data.startswith('back_to_service ')))

	dp.register_message_handler(c_admin, lambda message:'Связаться с администратором' in message.text)
	dp.register_message_handler(c_company, lambda message:'О компании' in message.text)

	dp.register_message_handler(test_scheduler_command, commands=['test_scheduler'])