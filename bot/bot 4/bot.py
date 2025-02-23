import aiosqlite
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройка бота
API_TOKEN = "6070517690:AAFp6YIzCHvEcYjYICFwhj4H8sg-Du8M8Ys"
url = 'https://script.google.com/macros/s/AKfycbxjreTKgCmtV_u2ha6-KgZBvlmle1R62cPikvmdzr98j4gpzHsY_8Ofl-w_ynIRwU4p/exec'  # Замените на URL вашего веб-приложения
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание базы данных и таблицы
async def create_db():
    async with aiosqlite.connect('users.db') as db:
        await db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, phone TEXT UNIQUE);')
        await db.commit()

# Состояния
class Form(StatesGroup):
    name = State()
    phone = State()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Введите ваше имя:")
    await Form.name.set()

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Введите ваш телефон:")
    await Form.phone.set()

@dp.message_handler(state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data['name']
    phone = message.text

    async with aiosqlite.connect('users.db') as db:
        # Проверка на дублирование номера телефона
        async with db.execute('SELECT phone FROM users WHERE phone = ?', (phone,)) as cursor:
            existing_number = await cursor.fetchone()
            if existing_number:
                await message.reply("Этот номер телефона уже существует. Пожалуйста, введите другой номер.")
                return

        # Добавление данных в базу данных
        await db.execute('INSERT INTO users (name, phone) VALUES (?, ?)', (name, phone))
        await db.commit()

        # Отправка данных в Google Таблицу
        async with aiohttp.ClientSession() as session:
            payload = {'name': name, 'phone': phone}
            async with session.post(url, data=payload) as resp:
                if resp.status == 200:
                    await message.reply("Ваши данные успешно добавлены и отправлены в Google Таблицу!")
                else:
                    await message.reply("Произошла ошибка при отправке данных в Google Таблицу.")

        await state.finish()

@dp.message_handler(commands=['users'])
async def list_users(message: types.Message):
    async with aiosqlite.connect('users.db') as db:
        async with db.execute('SELECT * FROM users') as cursor:
            users = await cursor.fetchall()
            await message.answer("Список пользователей:")
            if users:
                for user in users:
                    response = f"Имя: {user[1]}\nТелефон: {user[2]}\n"
                    await message.answer(response, reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Напоминание', callback_data=f'reminder {user[0]}')))
            else:
                await message.answer("Нет сохраненных пользователей.")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                response_message = "Данные из Google Таблицы:\n"
                for row in data:
                    response_message += f"Имя: {row[0]}\nТелефон: {row[1]}\n"  # Измените индексы в зависимости от структуры вашей таблицы
                await message.answer(response_message)
            else:
                await message.answer("Произошла ошибка при получении данных.")

#----------------------------------------------------------------------------------------------------------------------------------------------------------                

# Вывод одним сообщением
@dp.message_handler(commands=['usersg'])
async def list_users_google(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                await message.answer("Список пользователей (Google):")
                response_message = "Данные из Google Таблицы:\n"
                for row in data:
                    response_message += f"Имя: {row[0]}\nТелефон: {row[1]}\n"  # Измените индексы в зависимости от структуры вашей таблицы
                await message.answer(response_message)
            else:
                await message.answer("Произошла ошибка при получении данных.")

# Вывод 1 сообщение = 1 пользователь
@dp.message_handler(commands=['usersg2'])
async def list_users_google2(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                await message.answer("Список пользователей (Google):")
                for row in data:
                    response_message = f"Имя: {row[0]}\nТелефон: {row[1]}\n"  # Измените индексы в зависимости от структуры вашей таблицы
                    await message.answer(response_message, reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Напоминание', callback_data=f'reminderg {row[0]}')))
            else:
                await message.answer("Произошла ошибка при получении данных.")

#----------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())
    executor.start_polling(dp, skip_updates=True)