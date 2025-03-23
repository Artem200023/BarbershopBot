from flask import Flask
from flask import request
from flask import jsonify # 
import requests
import json
#from flask_sslify import SSLify # Не обязательно. На локалке не надо

app = Flask(__name__)
#sslify = SSLify(app) # Не обязательно. На локалке не надо

TOKEN = '7850327724:AAGhx7MJ2dnsnpejP_aw6uhmhRjPoMGf1t8'
# https://api.telegram.org/bot7850327724:AAGhx7MJ2dnsnpejP_aw6uhmhRjPoMGf1t8/setWebhook?url=https://artemptichenko.pythonanywhere.com/ - Активировать Webhook
# https://api.telegram.org/bot7850327724:AAGhx7MJ2dnsnpejP_aw6uhmhRjPoMGf1t8/deleteWebhook - Удалить Webhook
URL = 'https://api.telegram.org/bot7850327724:AAGhx7MJ2dnsnpejP_aw6uhmhRjPoMGf1t8/'

def write_json(data, filename='answer.json'):
	with open(filename, 'w', encoding='utf-8') as f:
		json.dump(data, f, indent=2, ensure_ascii=False)

def send_message(chat_id,text="bla-bla-bla"):
	url = URL + 'sendMessage'
	answer = {'chat_id': chat_id, 'text': text}
	r = requests.post(url, json=answer)
	return r.json()

def get_func():
	url = 'https://jsonplaceholder.typicode.com/users'
	r = requests.get(url).json() # requests.get(url) - Вызывает Responce объект, вызываем метод .json() и вся эта конструкция вызывает нужный словарь
	email_list = [user['email'] for user in r] # Вывод всех email

	return email_list

#@app.route('/bot{TOKEN}', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
# https://api.telegram.org/bot7850327724:AAGhx7MJ2dnsnpejP_aw6uhmhRjPoMGf1t8/setWebhook?url=https://artemptichenko.pythonanywhere.com/ - Активировать Webhook
# https://api.telegram.org/bot7850327724:AAGhx7MJ2dnsnpejP_aw6uhmhRjPoMGf1t8/setWebhook?url=https://726b-219-100-37-244.ngrok-free.app/ - Активация webHooka нужно вписать в браузере
# curl -X POST "https://api.telegram.org/bot7850327724:AAGhx7MJ2dnsnpejP_aw6uhmhRjPoMGf1t8/setWebhook?url=https://138c-219-100-37-244.ngrok-free.app/"
def index():
	if request.method == 'POST':
		r = request.get_json() # # Получаем данные от Telegram в формате json
		chat_id = r['message']['chat']['id'] # id чата в которое нужно отправить сообщение
		message = r['message']['text'] # Конкретное сообщение на которое будем отвечать

		if 'bitcoin' in message:
			send_message(chat_id,text='Тут дорого пиздец')

		#write_json(r)
		
		elif 'email' in message:
			emails = get_func()
			for email in emails:
				send_message(chat_id, text=email)
		
		elif 'Салам' in message:
			printe = get_func()
			# Объединяем все email-адреса в одну строку, разделяя их символом новой строки
			email_message = '\n'.join(printe)  
			send_message(chat_id, text=printe)  # Отправляем одно сообщение
			
		elif 'Printe2' in message:
			printe = get_func()
			email_list = []
			for email in printe:
				email_list.append(email)  # Добавляем каждый email в список
			email_message = '\n'.join(email_list)  # Объединяем все email-адреса в одну строку
			send_message(chat_id, text=email_message)  # Отправляем одно сообщение

		return jsonify(r)

	return '<h1>Bot welcomes you<h1>'

if __name__ == '__main__':
	app.run()
