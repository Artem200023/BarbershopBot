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

HOST = '192.168.1.94'  # Замените на IP-адрес ваших весов
PORT = 5001            # Замените на порт, используемый вашими весами

# Инициализация словаря для хранения данных
#weights_data = {
    #'weights': []
#}

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

filename = 'Datas.txt'
measurement_count = 0  # Счетчик замеров
massa = 0              # Переменная для накопления массы
last_weight = 0
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(full_message)

            s.settimeout(10)  
            data = s.recv(1024)
    
            if data:
                set_weight_bytes = data[6:10]   # Масса нетто
                set_stable_byte = data[11]      # Стабилизация
                set_zero_byte = data[13]        # >0< 

                if set_zero_byte != 1:
                    #print("\nУстановите на весах 0 г.")
                            
                    while True:  
                        s.sendall(full_message)
                        data = s.recv(1024)
                        if data:
                            set_weight_bytes = data[6:10]
                            set_stable_byte = data[11]
                            set_zero_byte = data[13]

                            set_weight = struct.unpack('<I', set_weight_bytes)[0]

                            if 800 <= set_weight <= 1200 and set_stable_byte == 1:
                                if set_stable_byte == 1: 
                                    last_weight = set_weight
                                    #print(f"{last_weight}")

                            #print(f"Данные сообщения: {data.hex()} (Длина ответа: {len(data)})")

                            #if set_zero_byte == 1 or (0 <= set_weight <= 50) or set_weight > 10000:
                            if set_zero_byte == 1 or (last_weight >= set_weight + 750) or set_weight > 10000:
                                if last_weight != 0:
                                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    massa += last_weight
                                    measurement_count += 1
                                    output_string = f"{current_time}\nЗамер {measurement_count}: Масса нетто : {last_weight} г - Сумарный вес : {massa} г\n"
                                    #print(current_time)
                                    print(f"\r{output_string}", end='')  # Обновляем строку в терминале
                                    write_to_file(filename, output_string)
                                    #print("\nПродолжайте замеры")
                                    last_weight = 0
                                    break
                                else:
                                    break
                  

            else:
                print("Ответ неполучен.")        
        except socket.timeout:
            print("Время ожидания ответа истекло.")
        except Exception as e:
            print(f"Ошибка: {e}")