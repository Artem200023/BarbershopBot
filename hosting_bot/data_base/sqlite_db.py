import sqlite3 as sq
from create_bot import bot

#--------------------------------------База данных для меню----------------------------------------------

def sql_start():
	global base, cur # base - переменная к файлу, cur - курсор перемещения по данным в файле
	base = sq.connect('barber_cool.db')
	cur = base.cursor()
	if base:
		print('Data base connected OK!')
	# CREATE TABLE/IF NOT EXISTS - Создать таблицу/если такой не существует, PRIMARY KEY - Повторяться название не будет
	base.execute('CREATE TABLE IF NOT EXISTS menu(img TEXT, name TEXT PRIMARY KEY, description TEXT, price TEXT)')
	base.commit()

async def sql_add_command(state):
	async with state.proxy() as data: # Открытие словаря куда записываются данные
		cur.execute('INSERT INTO menu VALUES (?, ?, ?, ?)', tuple(data.values())) #INSERT INTO menu VALUES вставляем значения, (?, ?, ?, ?) - для безопасного вставления, tuple(data.values())) - подставляем это значение
		base.commit()


async def sql_read(message):
		for ret in cur.execute('SELECT * FROM menu').fetchall():
			await bot.send_photo(message.from_user.id, ret[0], f'Название: {ret[1]}\nОписание: {ret[2]}\nЦена: {ret[-1]}')

async def sql_read2():
	return cur.execute('SELECT * FROM menu').fetchall()


async def sql_delete_command(data):
	cur.execute('DELETE FROM menu WHERE name == ?', (data,))
	base.commit()

#--------------------------------------База данных для мастеров------------------------------------------

def sql_masters():
	global base_master, cur_master # base - переменная к файлу, cur - курсор перемещения по данным в файле
	base_master = sq.connect('masters.db')
	cur_master = base_master.cursor()
	if base:
		print('Data base masters connected OK!')

	base_master.execute('CREATE TABLE IF NOT EXISTS masterslenina(img TEXT, name TEXT PRIMARY KEY, exp TEXT, location TEXT)')
	base_master.execute('CREATE TABLE IF NOT EXISTS mastersfrynze(img TEXT, name TEXT PRIMARY KEY, exp TEXT, location TEXT)')
	base_master.commit()

async def sql_add_commandlenina(state):
	async with state.proxy() as data: # Открытие словаря куда записываются данные
		cur_master.execute('INSERT INTO masterslenina VALUES (?, ?, ?, ?)', tuple(data.values())) #INSERT INTO menu VALUES вставляем значения, (?, ?, ?, ?) - для безопасного вставления, tuple(data.values())) - подставляем это значение
		base_master.commit()

async def sql_add_commandfrynze(state):
	async with state.proxy() as data: # Открытие словаря куда записываются данные
		cur_master.execute('INSERT INTO mastersfrynze VALUES (?, ?, ?, ?)', tuple(data.values())) #INSERT INTO menu VALUES вставляем значения, (?, ?, ?, ?) - для безопасного вставления, tuple(data.values())) - подставляем это значение
		base_master.commit()

#async def sql_read21(message):
		#for ret in cur21.execute('SELECT * FROM masters').fetchall():
			#await bot.send_photo(message.from_user.id, ret[0], f'Название: {ret[1]}\nОписание: {ret[2]}\nЦена: {ret[-1]}')

async def sql_readlenina():
	return cur_master.execute('SELECT * FROM masterslenina').fetchall()

async def sql_readfrynze():
	return cur_master.execute('SELECT * FROM mastersfrynze').fetchall()


async def sql_delete_commandlenina(data):
	cur_master.execute('DELETE FROM masterslenina WHERE name == ?', (data,))
	base_master.commit()

async def sql_delete_commandfrynze(data):
	cur_master.execute('DELETE FROM mastersfrynze WHERE name == ?', (data,))
	base_master.commit()

#--------------------------------------База данных для клиентов------------------------------------------

# Создание таблицы для хранения пользователей, если она не существует
def sql_clients():
	global base_client, cur_client
	base_client = sq.connect('clients.db')
	cur_client = base_client.cursor()
	if base:
		print('Data base clients connected OK!')
	
	base_client.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, phone TEXT)''')
	base_client.commit()

async def sql_add_command_clients(user_id, username, phone):
	cur_client.execute('INSERT INTO users (user_id, username, phone) VALUES (?, ?, ?)', (user_id, username, phone))
	base_client.commit()

async def is_phone_subscribed_clients(phone):
    cur_client.execute('SELECT * FROM users WHERE phone = ?', (phone,))
    return cur_client.fetchone() is not None  # Возвращает True, если пользователь найден