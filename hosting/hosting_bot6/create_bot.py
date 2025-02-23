from aiogram import Bot
from yclients import YClientsAPI # Yclients
#import pandas as pd # Yclients
from aiogram.dispatcher import Dispatcher
import config1

# Хранилище
from aiogram.contrib.fsm_storage.memory import MemoryStorage 

storage=MemoryStorage()

bot = Bot(token=config1.TOKEN)
api = YClientsAPI(token=config1.TOKENY, company_id=config1.СID, form_id=config1.FID)#, debug=True) # Yclients



dp = Dispatcher(bot, api, storage=storage)