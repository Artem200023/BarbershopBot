import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from data_base import sqlite_db

class BirthdayService:
    def __init__(self, bot, dp):
        self.bot = bot
        self.dp = dp
        self.scheduler = AsyncIOScheduler()
    
    async def send_birthday_congratulations(self, user_id, username):
        try:
            message = f"🎉 Дорогой(ая) {username}!\n\nС Днем рождения! 🎂"
            await self.bot.send_message(user_id, message)
            print(f"✅ Поздравление отправлено {username}")
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки {username}: {e}")
            return False
    
    async def daily_birthday_check(self):
        try:
            print(f"🕐 Проверка дней рождения в {datetime.now().strftime('%H:%M:%S')}")
            try:
                birthdays = await sqlite_db.get_todays_birthdays()
            except Exception as e:
                print(f"❌ Ошибка при получении данных из БД: {e}")
                return           

            if birthdays:
                print(f"🎂 Найдено {len(birthdays)} именинников! Отправляем поздравления...")
                for user_id, username, birth_date in birthdays:
                    await self.send_birthday_congratulations(user_id, username)
                    await asyncio.sleep(1)
            else:
                print("📭 Сегодня нет именинников")
        except Exception as e:
            print(f"❌ Критическая ошибка в daily_birthday_check: {e}")

    def setup_scheduler(self):
        try:
            # ✅ ДОБАВЬТЕ ЭТУ ПРОВЕРКУ
            if self.scheduler.running:
                print("⚠️ Планировщик уже запущен, пропускаем инициализацию")
                return
        
            # ✅ ПРОВЕРКА СУЩЕСТВУЮЩИХ ЗАДАЧ
            existing_jobs = self.scheduler.get_jobs()
            if existing_jobs:
                print(f"⚠️ Задачи уже добавлены: {[job.id for job in existing_jobs]}")
                return
        
            # ✅ Добавляем задачи в планировщик
            self.scheduler.add_job(
                self.daily_birthday_check,
                CronTrigger(hour=22, minute=34),
                id='morning_birthday_check'
            )
        
            self.scheduler.add_job(
                self.daily_birthday_check,
                CronTrigger(hour=22, minute=35),
                id='afternoon_birthday_check'
            )
        
            self.scheduler.add_job(
                self.daily_birthday_check,
                CronTrigger(hour=22, minute=36),
                id='evening_birthday_check'
            )
        
            # ✅ Запускаем планировщик
            self.scheduler.start()
            print("🚀 APScheduler запущен! Проверки в 21:32, 21:33, 22:08")
        
        except Exception as e:
            print(f"❌ Критическая ошибка при запуске планировщика: {e}")

def setup_birthday_scheduler(bot, dp):
    service = BirthdayService(bot, dp)
    service.setup_scheduler()
    return service