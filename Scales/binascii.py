import socket
import struct
import time
from datetime import datetime  # Импортируем модуль datetime
import os
import sys

import pandas as pd  # Добавлено для работы с Excel

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if (crc & 0x0001) != 0:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def append_to_excel(filename, data_dict):
    """
    Записывает данные из словаря data_dict в Excel-файл filename.
    Если файл не существует — создаёт новый с заголовками.
    """
    import openpyxl  # импорт здесь, чтобы не грузить если не нужно
    
    if not os.path.exists(filename):
        # Создаем новый файл и пишем заголовки и первую строку данных
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(list(data_dict.keys()))  # Заголовки столбцов
        ws.append(list(data_dict.values()))  # Данные
        wb.save(filename)
        #text_area.insert(tk.END, f"Файл {filename} создан и данные записаны.\n")
    else:
        # Открываем существующий файл и добавляем строку данных
        wb = openpyxl.load_workbook(filename)
        ws = wb.active
        ws.append(list(data_dict.values()))
        wb.save(filename)
        #text_area.insert(tk.END, f"Данные добавлены в файл {filename}.\n")

def process_weight(last_weight, massa, measurement_count, massa1, measurement_count1, massaw, measurement_count_weight,good_last_weight ,bad_last_weight):
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_time_date = datetime.now().strftime("%Y-%m-%d")
    current_time_time = datetime.now().strftime("%H:%M:%S")
    measurement_count_weight += 1
    massaw += last_weight
    filename_excel = 'Datas.xlsx' 

    if 1000 <= last_weight <= 1020:
        massa += last_weight
        measurement_count += 1
        good_last_weight = last_weight
        output_string = f"{current_time}\nЗамер {measurement_count} ({measurement_count_weight}): Масса нетто : {last_weight} г - Сумарный вес : {massa} г ({massaw} г)\n"
        print(f"\r{output_string}", end='')  # Обновляем строку в терминале
        
        #return massa, measurement_count, last_weight, massa1, measurement_count1, massaw, measurement_count_weight  # Возвращаем также massa1 и measurement_count1

    else:  
        massa1 += last_weight
        measurement_count1 += 1
        bad_last_weight = last_weight
        output_string1 = f"{current_time}\nЗамер {measurement_count1} ({measurement_count_weight}): Масса нетто : {last_weight} г - Сумарный вес : {massa1} г ({massaw} г)\n"
        print(f"\r{output_string1}", end='')  # Обновляем строку в терминале

    # Запись данных сразу в Excel-файл 
    append_to_excel(filename_excel, {
        'Дата': current_time_date,
        'Время': current_time_time,   
        'Вес норма (г)': good_last_weight,
        'Замер норма': measurement_count if good_last_weight > 0 else 0,
        'Вес не норма (г)': bad_last_weight,
        'Замер не норма': measurement_count1 if bad_last_weight > 0 else 0,
        'Кол-во замеров': measurement_count_weight,
        'Весь суммарный вес (г)': massaw,
        'Суммарный вес норма (г)': massa,
        'Суммарный вес не норма (г)': massa1,
    })

    last_weight = 0
    good_last_weight = 0
    bad_last_weight = 0


    return massa, measurement_count, last_weight, massa1, measurement_count1, massaw, measurement_count_weight, good_last_weight, bad_last_weight  # Возвращаем также massa и measurement_count


HOST = '192.168.1.94'  # Замените на IP-адрес ваших весов
PORT = 5001            # Замените на порт, используемый вашими весами

# Формирование сообщения для запроса массы
header = bytes([0xF8, 0x55, 0xCE])
length = struct.pack('<H', 0x0001)  # Длина тела сообщения
command = bytes([0x23])              # Код команды CMD_GET_MASSA

# Полное сообщение без CRC
message = header + length + command

# Вычисляем CRC на основе команды и длины
crc = calculate_crc(message[3:])  
crc_bytes = struct.pack('<H', crc)

# Полное сообщение с CRC
full_message = message + crc_bytes

# Команда установки 0
command_reset_zero = bytes([0x72])   
message_reset_zero = header + length + command_reset_zero
crc_reset_zero = calculate_crc(message_reset_zero[3:])  
crc_bytes_reset_zero = struct.pack('<H', crc_reset_zero)
full_message_reset_zero = message_reset_zero + crc_bytes_reset_zero

#Показания которые соответствуют норме
measurement_count = 0  
massa = 0
good_last_weight = 0

#Показания которые не соответствуют норме
measurement_count1 = 0 
massa1 = 0

# Суммарные показания
measurement_count_weight = 0
massaw = 0 
bad_last_weight = 0

last_weight = 0

         
while True:
    attempts = 5   # Переменная attempts теперь объявлена здесь для доступа в цикле.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(full_message)

            s.settimeout(10)  
            data = s.recv(1024)
    
            if data:
                set_weight_bytes = data[6:10]   
                set_stable_byte = data[11]      
                set_zero_byte = data[13]        

                if set_zero_byte != 1:
                    attempts = 5  # Сброс attempts перед началом цикла
                    while attempts > 0:   
                        s.sendall(full_message)
                        data = s.recv(1024)
                        if data:
                            set_weight_bytes = data[6:10]
                            set_stable_byte = data[11]
                            set_zero_byte = data[13]

                            set_weight = struct.unpack('<I', set_weight_bytes)[0]

                            if (800 <= set_weight <= 1200 and set_stable_byte == 1):
                                if set_stable_byte == 1: 
                                    last_weight = set_weight

                            if set_zero_byte == 1 or (0 <= set_weight <= 100) or set_weight > 10000:
                            #if set_zero_byte == 0:
                                #massa, measurement_count, last_weight = process_weight(last_weight, massa, measurement_count, filename, massa1, measurement_count1, filename1)
                                if last_weight != 0:
                                    massa, measurement_count, last_weight, massa1, measurement_count1, massaw, measurement_count_weight, good_last_weight, bad_last_weight = process_weight(last_weight, massa, measurement_count, massa1, measurement_count1, massaw, measurement_count_weight, good_last_weight, bad_last_weight)
                                    break
                                else:
                                    break
                attempts -= 1

            else:
                print("Ответ не получен.")        
        except socket.timeout:
            print("Время ожидания ответа истекло.")
        except Exception as e:
            print(f"Ошибка: {e}")


