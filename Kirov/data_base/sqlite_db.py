import sqlite3 as sq
from create_bot import bot

def sql_clients():
	global base_client, cur_client
	base_client = sq.connect('clients.db')
	cur_client = base_client.cursor()
	if base_client:
		print('Data base clients connected OK!')
	
	base_client.execute('''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, username TEXT, phone TEXT)''')
	base_client.commit()

async def sql_add_command_clients(user_id, username, phone):
	cur_client.execute('INSERT INTO users (user_id, username, phone) VALUES (?, ?, ?)', (user_id, username, phone))
	base_client.commit()

async def is_phone_subscribed_clients(phone):
    cur_client.execute('SELECT * FROM users WHERE phone = ?', (phone,))
    return cur_client.fetchone() is not None  # Возвращает True, если пользователь найден

# Показать данные клиентов
async def sql_read_name_clients():
	return cur_client.execute('SELECT * FROM users').fetchall()

#--------------------------------------База данных для акций------------------------------------------

def sql_newsletter():
	global base_promotion, cur_promotion # base - переменная к файлу, cur - курсор перемещения по данным в файле
	base_promotion = sq.connect('promotions.db')
	cur_promotion = base_promotion.cursor()
	if base_promotion:
		print('Data base promotions connected OK!')

	base_promotion.execute('CREATE TABLE IF NOT EXISTS promotions(pid INTEGER PRIMARY KEY AUTOINCREMENT ,name TEXT, img TEXT, description TEXT)')
	base_promotion.commit()

async def sql_send_command_promotion(data):
	# 1 cur_promotion.execute('SELECT FROM promotions WHERE name == ?', (data,))
	cur_promotion.execute('SELECT name, img, description FROM promotions WHERE pid = ?', (data,))
	promotion = cur_promotion.fetchone()
	return promotion
	#base_promotion.close()

# Добавить акцию
async def sql_add_command_promotion(state):
    async with state.proxy() as data:
        # Указываем только те столбцы, которые мы хотим заполнить
        cur_promotion.execute('INSERT INTO promotions (name, img, description) VALUES (?, ?, ?)', 
                              (data['name'], data['img'], data['description'])) 
        base_promotion.commit()

# Показать данные акциии
async def sql_read_text_promotion(message):
		for ret in cur_promotion.execute('SELECT * FROM promotions').fetchall():
			await bot.send_photo(message.from_user.id, ret[0], f'Описание: {ret[1]}')

# Показать данные акциии
async def sql_read_promotion():
	return cur_promotion.execute('SELECT * FROM promotions').fetchall()

# Удалить акцию
async def sql_del_command_promotion(data):
	cur_promotion.execute('DELETE FROM promotions WHERE pid == ?', (data,))
	base_promotion.commit()



