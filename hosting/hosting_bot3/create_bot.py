from aiogram import Bot
#from yclients import YClientsAPI # Yclients
#import pandas as pd # Yclients
from aiogram.dispatcher import Dispatcher
import config1

# Хранилище
from aiogram.contrib.fsm_storage.memory import MemoryStorage 

storage=MemoryStorage()
                               # Yclients
bot = Bot(token=config1.TOKEN)#, company_id="829934", form_id=config1.FID, debug=True)
#api = YClientsAPI(token=TOKENY, company_id=СID, form_id=FID, debug=True) # Yclients


dp = Dispatcher(bot, storage=storage)