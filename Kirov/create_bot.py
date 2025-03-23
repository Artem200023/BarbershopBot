from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import config
#import pandas as pd # Yclients

# Хранилище
from aiogram.contrib.fsm_storage.memory import MemoryStorage 

storage=MemoryStorage()

bot = Bot(token=config.TOKEN)

dp = Dispatcher(bot, storage=storage)