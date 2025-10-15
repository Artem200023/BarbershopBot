import sqlite3 as sq
from create_bot import bot
from datetime import datetime, date

#--------------------------------------База данных для клиентов------------------------------------------

def get_db_connection():
    """Создает новое соединение с БД (потокобезопасно)"""
    connection = sq.connect('clients.db', check_same_thread=False)
    return connection

def sql_clients():
    """Инициализация таблицы (вызывается в основном потоке)"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        phone TEXT, 
        birth_date TEXT
    )''')
    connection.commit()
    connection.close()
    print('Data base clients connected OK!')
#---------------------------------------------------------------------------------------------
async def sql_add_command_clients(user_data):
    """Добавление пользователя из web-формы"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        values = (
            int(user_data['user_id']),
            user_data['username'],
            user_data['phone'], 
            user_data['birth_date']
        )
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', values)
        connection.commit()
        print(f"✅ Пользователь {user_data['username']} успешно добавлен в базу")
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении пользователя: {e}")
        return False
    finally:
        connection.close()
#---------------------------------------------------------------------------------------------
async def is_user_subscribed_clients(user_id):
    """Проверка подписки пользователя"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone() is not None
    
    connection.close()
    return result

async def sql_read_name_clients():
    """Чтение всех клиентов"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    result = cursor.execute('SELECT * FROM users').fetchall()
    connection.close()
    return result

# Функция для получения пользователей, у которых сегодня день рождения
async def get_todays_birthdays():
    """Получение именинников (потокобезопасно)"""
    today = date.today()
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT user_id, username, birth_date FROM users')
    all_users = cursor.fetchall()
    
    birthdays_today = []
    for user in all_users:
        user_id, username, birth_date_str = user
        if birth_date_str:
            try:
                #if '-' in birth_date_str:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
                
                if birth_date.month == today.month and birth_date.day == today.day:
                    birthdays_today.append((user_id, username, birth_date_str))
                    print(f"🎂 Найден именинник: {username} - {birth_date_str}")
            except ValueError as e:
                print(f"❌ Неверный формат даты для пользователя {user_id}: {birth_date_str} - Ошибка: {e}")
                continue
    
    connection.close()
    print(f"📊 Всего найдено именинников: {len(birthdays_today)}")
    return birthdays_today

#--------------------------------------База данных для акций------------------------------------------
def get_promotion_connection():
    """Создает новое соединение с promotions БД (потокобезопасно)"""
    connection = sq.connect('promotions.db', check_same_thread=False)
    return connection

def sql_newsletter():
    """Инициализация таблицы promotions"""
    connection = get_promotion_connection()
    cursor = connection.cursor()


    cursor.execute('CREATE TABLE IF NOT EXISTS promotions(pid INTEGER PRIMARY KEY AUTOINCREMENT ,name TEXT, img TEXT, description TEXT)')
    connection.commit()
    connection.close()
    print('Data base promotions connected OK!')

async def sql_send_command_promotion(data):
    """Получить акцию по ID"""
    connection = get_promotion_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT name, img, description FROM promotions WHERE pid = ?', (data,))
        promotion = cursor.fetchone()
        return promotion
    except Exception as e:
        print(f"❌ Ошибка получения акции {data}: {e}")
        return None
    finally:
        connection.close()
          
# Добавить акцию
async def sql_add_command_promotion(state):
    """Добавить акцию"""
    connection = get_promotion_connection()
    cursor = connection.cursor()
    try:
        async with state.proxy() as data:
            # Указываем только те столбцы, которые мы хотим заполнить
            cursor.execute('INSERT INTO promotions (name, img, description) VALUES (?, ?, ?)', 
                              (data['name'], data['img'], data['description'])) 
            connection.commit()
            return True
    except Exception as e:
        print(f"❌ Ошибка добавления акции: {e}")
        return False
    finally:
        connection.close()
# Показать данные акциии
async def sql_read_text_promotion(message):
    """Показать акции с отправкой фото"""
    connection = get_promotion_connection()
    cursor = connection.cursor()
    try:
        for ret in cursor.execute('SELECT * FROM promotions').fetchall():
            await bot.send_photo(message.from_user.id, ret[2], f'Описание: {ret[3]}')
    except Exception as e:
        print(f"❌ Ошибка отправки акций: {e}")
    finally:
        connection.close()
# Показать данные акциии
async def sql_read_promotion():
    """Получить все акции"""
    connection = get_promotion_connection()
    cursor = connection.cursor()
    try:
        return cursor.execute('SELECT * FROM promotions').fetchall()
    except Exception as e:
        print(f"❌ Ошибка чтения акций: {e}")
        return []
    finally:
        connection.close()
# Удалить акцию
async def sql_del_command_promotion(data):
     
    """Удалить акцию"""
    connection = get_promotion_connection()
    cursor = connection.cursor()
    try:   
        cursor.execute('DELETE FROM promotions WHERE pid == ?', (data,))
        connection.commit()
        print(f"✅ Акция {data} удалена")
        return True
    except Exception as e:
        print(f"❌ Ошибка удаления акции {data}: {e}")
        return False
    finally:
        connection.close()
#--------------------------------------База данных для услуг------------------------------------------
def get_services_connection():
    """Создает новое соединение с services БД (потокобезопасно)"""
    connection = sq.connect('services.db', check_same_thread=False)
    return connection

def sql_services():
    """Инициализация таблицы services"""
    connection = get_services_connection()
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS services(pid INTEGER PRIMARY KEY AUTOINCREMENT ,name TEXT, img TEXT)')
    connection.commit()
    connection.close()
    print('Data base services connected OK!')

async def sql_send_command_services(data):
    """Получить услугу по ID"""
    connection = get_services_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT name, img FROM services WHERE pid = ?', (data,))
        services = cursor.fetchone()
        return services
    except Exception as e:
        print(f"❌ Ошибка получения услуги {data}: {e}")
        return None
    finally:
        connection.close()

# Добавить услугу
async def sql_add_command_services(state):
    """Добавить акцию"""
    connection = get_services_connection()
    cursor = connection.cursor()
    try:
        async with state.proxy() as data:
            # Указываем только те столбцы, которые мы хотим заполнить
            cursor.execute('INSERT INTO services (name, img) VALUES (?, ?)', 
                              (data['name'], data['img'])) 
            connection.commit()
            print(f"✅ Услуга '{data['name']}' добавлена")
            return True
    except Exception as e:
        print(f"❌ Ошибка добавления услуги: {e}")
        return False
    finally:
        connection.close()

# Показать данные услуг
async def sql_read_text_services(message):
    """Показать услуги с отправкой фото (для админа)"""
    connection = get_services_connection()
    cursor = connection.cursor()
    try:
        for ret in cursor.execute('SELECT * FROM services').fetchall():
            await bot.send_photo(message.from_user.id, ret[2], f'{ret[1]}')
    except Exception as e:
        print(f"❌ Ошибка отправки услуг: {e}")
    finally:
        connection.close()
# Показать данные услуг
async def sql_read_services():
    """Получить все услуги"""
    connection = get_services_connection()
    cursor = connection.cursor()
    try:
        return cursor.execute('SELECT * FROM services').fetchall()
    except Exception as e:
        print(f"❌ Ошибка чтения услуг: {e}")
        return []
    finally:
        connection.close()
# Удалить услугу
async def sql_del_command_services(data):
    """Удалить услугу"""
    connection = get_services_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('DELETE FROM services WHERE pid == ?', (data,))
        connection.commit()
        print(f"✅ Услуга {data} удалена")
        return True
    except Exception as e:
        print(f"❌ Ошибка удаления услуги {data}: {e}")
        return False
    finally:
        connection.close()


