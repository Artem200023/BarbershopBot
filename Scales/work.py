import socket
import struct
import time
from datetime import datetime  # Импортируем модуль datetime

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

def write_to_file(filename, data):
    with open(filename, 'a', encoding='utf-8') as file:  # Открываем файл для добавления данных
        file.write(data + '\n')  # Записываем данные в файл с новой строки

def write_to_file1(filename1, data):
    with open(filename1, 'a', encoding='utf-8') as file:  # Открываем файл для добавления данных
        file.write(data + '\n')  # Записываем данные в файл с новой строки

def process_weight(last_weight, massa, measurement_count, filename, massa1, measurement_count1, filename1, massaw, measurement_count_weight):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    measurement_count_weight += 1
    massaw += last_weight 
    if 1000 <= last_weight <= 1020:
        massa += last_weight
        measurement_count += 1
        output_string = f"{current_time}\nЗамер {measurement_count} ({measurement_count_weight}): Масса нетто : {last_weight} г - Сумарный вес : {massa} г ({massaw} г)\n"
        print(f"\r{output_string}", end='')  # Обновляем строку в терминале
        write_to_file(filename, output_string)
        last_weight = 0
        return massa, measurement_count, last_weight, massa1, measurement_count1, massaw, measurement_count_weight  # Возвращаем также massa1 и measurement_count1

    else:  
        massa1 += last_weight
        measurement_count1 += 1
        output_string1 = f"{current_time}\nЗамер {measurement_count1} ({measurement_count_weight}): Масса нетто : {last_weight} г - Сумарный вес : {massa1} г ({massaw} г)\n"
        print(f"\r{output_string1}", end='')  # Обновляем строку в терминале
        write_to_file1(filename1, output_string1)
        last_weight = 0
        return massa, measurement_count, last_weight, massa1, measurement_count1, massaw, measurement_count_weight  # Возвращаем также massa и measurement_count


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

filename = 'Good.txt'
filename1 = 'Bad.txt'
measurement_count = 0  
massa = 0
measurement_count1 = 0 
massa1 = 0
measurement_count_weight = 0
massaw = 0                 
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
                                    massa, measurement_count, last_weight, massa1, measurement_count1, massaw, measurement_count_weight = process_weight(last_weight, massa, measurement_count, filename, massa1, measurement_count1, filename1, massaw, measurement_count_weight)
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


