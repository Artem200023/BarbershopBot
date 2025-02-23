import sqlite3 as sq
from create_bot import bot

#------------------------------База данных для меню----------------------------------------------
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
#-------------------------------База данных для заявки------------------------------------------


