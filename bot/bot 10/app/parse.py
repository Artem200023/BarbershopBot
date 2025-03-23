import requests
from main import write_json # импортируем с файла main.py функцию write_json

def get_func():
	# 1) r = requests.get(url) # requests.get(url) - Вызывает Responce объект, можно вызвать метод .json()
	# 2) name = r[0]['email'] # Обращаемся к первому элементу в списке и к ключу email
	# 3) write_json(r.json(), filename='price.json') # Создастся файл в котором будут данные в json формате указанный в url
	url = 'https://jsonplaceholder.typicode.com/users'
	r = requests.get(url).json() # requests.get(url) - Вызывает Responce объект, вызываем метод .json() и вся эта конструкция вызывает нужный словарь
	email_list = [user['email'] for user in r] # Вывод всех email

return email_list

def main():
	#print(get_func())
	emails = get_func()  # Получаем список email-адресов
	for email in emails:  # Проходим по каждому email
		print(email)  # Выводим email в столбик

if __name__ == '__main__':
	main()