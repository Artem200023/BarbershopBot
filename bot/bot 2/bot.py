import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram_calendar import SimpleCalendar, simple_cal_callback

API_TOKEN = "6070517690:AAFp6YIzCHvEcYjYICFwhj4H8sg-Du8M8Ys"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Пример функции для создания календаря с выделением определенных дней
async def show_calendar(message: types.Message):
    calendar = SimpleCalendar()
    special_dates = {1, 15, 20}  # Пример: 1, 15 и 20 числа месяца

    # Создаем кнопки для дней месяца
    buttons = []
    for day in range(1, 32):  # Пример для месяца с 31 днем
        button_text = f"{day} ✅" if day in special_dates else str(day)
        buttons.append(types.InlineKeyboardButton(text=button_text, callback_data=f"day_{day}"))

    # Создаем разметку для кнопок
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    keyboard.add(*buttons)

    # Добавляем кнопки навигации
    navigation_buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="prev_month"),
        types.InlineKeyboardButton(text="▶️", callback_data="next_month")
    ]
    keyboard.add(*navigation_buttons)

    await message.answer("Выберите дату:", reply_markup=keyboard)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Используйте команду /calendar для выбора даты.")

@dp.message_handler(commands=['calendar'])
async def calendar_command(message: types.Message):
    await show_calendar(message)

@dp.callback_query_handler(simple_cal_callback.filter())
async def process_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    day = callback_data['day']
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"Вы выбрали: {day} число.")

@dp.callback_query_handler(lambda c: c.data in ["prev_month", "next_month"])
async def navigate_month(callback_query: types.CallbackQuery):
    # Здесь вы можете добавить логику для изменения месяца
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Навигация по месяцам еще не реализована.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)