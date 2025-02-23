import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# Вставьте сюда ваш токен бота
API_TOKEN = '7850327724:AAGhx7MJ2dnsnpejP_aw6uhmhRjPoMGf1t8'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Записаться", url="https://yclients.com/online_booking/829934/settings")
    keyboard.add(button)
    await message.answer('Выберите действие:', reply_markup=keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)