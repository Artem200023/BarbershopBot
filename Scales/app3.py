import socket
import struct
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import threading

# Глобальная переменная для остановки потока измерений
stop_measurement_flag = False

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
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(data + '\n')

def start_measurement():
    global stop_measurement_flag
    stop_measurement_flag = False  # Сброс флага остановки
    # Запуск измерений в отдельном потоке
    threading.Thread(target=measure).start()

def stop_measurement():
    global stop_measurement_flag
    stop_measurement_flag = True  # Установка флага остановки

def measure():
    global stop_measurement_flag
    
    HOST = '192.168.1.94'
    PORT = 5001

    header = bytes([0xF8, 0x55, 0xCE])
    length = struct.pack('<H', 0x0001)
    command = bytes([0x23])
    
    message = header + length + command
    crc = calculate_crc(message[3:])
    crc_bytes = struct.pack('<H', crc)
    full_message = message + crc_bytes

    filename = 'Datas.txt'
    measurement_count = 0
    massa = 0
    last_weight = 0

    connected_successfully = False  # Флаг успешного подключения

    while not stop_measurement_flag:  # Проверка флага остановки в цикле
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                if not connected_successfully:  # Если подключение успешно и еще не было сообщения об этом
                    text_area.insert(tk.END, "Подключение успешно.\n")
                    connected_successfully = True
                
                s.sendall(full_message)

                s.settimeout(10)
                data = s.recv(1024)

                if data:
                    set_weight_bytes = data[6:10]
                    set_stable_byte = data[11]
                    set_zero_byte = data[13]

                    if set_zero_byte != 1:
                        while not stop_measurement_flag:  
                            s.sendall(full_message)
                            data = s.recv(1024)
                            if data:
                                set_weight_bytes = data[6:10]
                                set_stable_byte = data[11]
                                set_zero_byte = data[13]

                                set_weight = struct.unpack('<I', set_weight_bytes)[0]

                                if 800 <= set_weight <= 1200 and set_stable_byte == 1:
                                    last_weight = set_weight

                                if set_zero_byte == 1 or (last_weight >= set_weight + 750) or set_weight > 10000:
                                    if last_weight != 0:
                                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        massa += last_weight
                                        measurement_count += 1
                                        output_string = f"{current_time}\nЗамер {measurement_count}: Масса нетто : {last_weight} г - Сумарный вес : {massa} г\n"
                                        
                                        # Обновление текстового поля в основном потоке GUI
                                        text_area.insert(tk.END, output_string)
                                        write_to_file(filename, output_string)
                                        last_weight = 0
                                        break

            except socket.timeout:
                if connected_successfully: 
                    text_area.insert(tk.END, "Время ожидания ответа истекло.\n")
            except Exception as e:
                text_area.insert(tk.END, f"Ошибка: {e}\n")
                connected_successfully = False

# Создание основного окна приложения
root = tk.Tk()
root.title("Весы")

# Создание текстового поля для вывода данных
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
text_area.pack(padx=10, pady=10)

# Кнопка для начала измерений
start_button = tk.Button(root, text="Начать измерение", command=start_measurement)
start_button.pack(pady=5)

# Кнопка для остановки измерений
stop_button = tk.Button(root, text="Остановить измерение", command=stop_measurement)
stop_button.pack(pady=5)

# Запуск основного цикла приложения
root.mainloop()