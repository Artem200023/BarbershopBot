import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import sqlite3
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import asyncio
from aiogram.dispatcher import FSMContext

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
API_TOKEN = "6070517690:AAFp6YIzCHvEcYjYICFwhj4H8sg-Du8M8Ys"
# ADMIN = 1123330844
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Подключение к базе данных SQLite
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создание таблицы для хранения пользователей, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    phone TEXT
)
''')
conn.commit()

scheduler = AsyncIOScheduler()

async def send_delayed_message(chat_id, text):
    await bot.send_message(chat_id, text)

def schedule_message(chat_id, text):
    # Запланировать отправку сообщения через 10 секунд
    scheduler.add_job(send_delayed_message, 'date', run_date=datetime.now() + timedelta(seconds=3), args=[chat_id, text])

# Функция для проверки, есть ли пользователь с таким номером телефона в базе данных
def is_phone_subscribed(phone):
    cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,))
    return cursor.fetchone() is not None  # Возвращает True, если пользователь найден

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Запрашиваем номер телефона у пользователя
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Подписаться", request_contact=True)
    markup.add(button_phone)

    await message.reply("Привет, подпишись на меня !", reply_markup=markup)

    schedule_message(message.chat.id, "Это сообщение отправлено через 3 секунды!")

@dp.message_handler(content_types=[types.ContentType.CONTACT])
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    phone = message.contact.phone_number

    if is_phone_subscribed(phone):
        await message.answer("Вы уже подписаны!", reply_markup=ReplyKeyboardRemove())
    else:
        # Сохранение информации о пользователе в базе данных
        cursor.execute('INSERT INTO users (user_id, username, phone) VALUES (?, ?, ?)', 
                       (user_id, username, phone))
        conn.commit()
        await message.answer("Вы успешно подписаны!", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(commands=['users'])
async def list_users(message: types.Message):
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    await message.answer("Список пользователей:")
    if users:
        for user in users:
            response = f"Имя : {user[1]}\nТелефон : {user[2]}\n"
            await message.answer(response, reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Напоминание', callback_data=f'reminder {user[0]}')))
    else:
        response = "Нет сохраненных пользователей."
    #sent_message = await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\n{ret[2]}',reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=f'Выбрать {ret[1]}', callback_data=f'master {ret[1]}')))
        #async with state.proxy() as data:

#@dp.callback_query_handler(lambda c: c.data == 'reminder')
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('reminder '))
async def process_callback_reminder(callback_query: types.CallbackQuery):
    TARGET_USER_ID = callback_query.data.replace(f"reminder ","")
    await bot.answer_callback_query(callback_query.id) # Что бы не было мигания после нажатия на инлайн кнопку
    #await bot.send_message(callback_query.from_user.id, "Привет")
    schedule_message(TARGET_USER_ID, "Напоминание")

@dp.message_handler(commands=['Рассылка'])
async def start_broadcast(message: types.Message):
    # Проверка, что сообщение отправлено администратором
    if message.from_user.id != 1123330844 and 841899262:  # Замените YOUR_ADMIN_ID на свой ID
        await message.reply("У вас нет прав для рассылки сообщений.")
        return
    
    await message.reply("Пожалуйста, введите текст для рассылки:")

    # Сохраняем состояние, чтобы знать, что ждем текст для рассылки
    await dp.current_state(user=message.from_user.id).set_state("waiting_for_broadcast_text")

@dp.message_handler(state="waiting_for_broadcast_text")
async def broadcast_message(message: types.Message, state: FSMContext):
    # Получаем текст для рассылки
    broadcast_text = message.text

    # Получение всех ID пользователей для рассылки
    cursor.execute('SELECT user_id FROM users')
    user_ids = cursor.fetchall()

    for user in user_ids:
        try:
            await bot.send_message(user[0], broadcast_text)
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user[0]}: {e}")

    await message.reply("Рассылка завершена.")

    # Сбрасываем состояние
    await state.finish()

@dp.message_handler(commands=['stop'])
async def stop_bot(message: types.Message):
    await message.reply("Бот остановлен.")
    # Закрытие соединения с базой данных
    conn.close()
    await dp.stop_polling()

async def on_startup(_):
    if not scheduler.running:
        scheduler.start()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup(dp))
    executor.start_polling(dp, skip_updates=True)