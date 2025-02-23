from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import config1

# Хранилище
from aiogram.contrib.fsm_storage.memory import MemoryStorage 

storage=MemoryStorage()

bot = Bot(token=config1.TOKEN)
dp = Dispatcher(bot, storage=storage)