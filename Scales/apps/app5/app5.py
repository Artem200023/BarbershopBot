import socket
import struct
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import threading

# Глобальные переменные для остановки потоков измерений
stop_measurement_flags = [False, False, False]

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

def start_measurement(index):
    global stop_measurement_flags
    stop_measurement_flags[index] = False  # Сброс флага остановки для данного устройства
    ip = ip_entries[index].get()
    port = int(port_entries[index].get())
    threading.Thread(target=measure, args=(index, ip, port)).start()

def stop_measurement(index):
    global stop_measurement_flags
    stop_measurement_flags[index] = True  # Установка флага остановки для данного устройства

def measure(index, ip, port):
    global stop_measurement_flags
    
    header = bytes([0xF8, 0x55, 0xCE])
    length = struct.pack('<H', 0x0001)
    command = bytes([0x23])
    
    message = header + length + command
    crc = calculate_crc(message[3:])
    crc_bytes = struct.pack('<H', crc)
    full_message = message + crc_bytes

    filename = f'Datas_{index}.txt'  # Файл для каждого устройства
    measurement_count = 0
    massa = 0
    last_weight = 0

    connected_successfully = False

    while not stop_measurement_flags[index]:  
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip, port))
                if not connected_successfully:  
                    text_area.insert(tk.END, f"Подключение успешно к устройству {index + 1} ({ip}:{port}).\n")
                    connected_successfully = True
                
                s.sendall(full_message)

                s.settimeout(10)
                data = s.recv(1024)

                if data:
                    set_weight_bytes = data[6:10]
                    set_stable_byte = data[11]
                    set_zero_byte = data[13]

                    if set_zero_byte != 1:
                        while not stop_measurement_flags[index]:  
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
                                        output_string = f"{current_time}\nУстройство {index + 1}: Замер {measurement_count}: Масса нетто : {last_weight} г - Сумарный вес : {massa} г\n"
                                        
                                        text_area.insert(tk.END, output_string)
                                        write_to_file(filename, output_string)
                                        last_weight = 0
                                        break

            except socket.timeout:
                if connected_successfully: 
                    text_area.insert(tk.END, f"Время ожидания ответа истекло для устройства {index + 1}.\n")
            except Exception as e:
                text_area.insert(tk.END, f"Ошибка на устройстве {index + 1}: {e}\n")
                connected_successfully = False

# Создание основного окна приложения
root = tk.Tk()
root.title("Весы")

# Создание текстового поля для вывода данных
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
text_area.pack(padx=10, pady=10)

# Списки для хранения полей ввода IP и порта и кнопок управления измерениями
ip_entries = []
port_entries = []

# Создание интерфейса для трех устройств с полями ввода IP и порта и кнопками управления измерениями
for i in range(3):
    frame_device = tk.Frame(root)
    
    label_device_id = tk.Label(frame_device, text=f"Устройство {i + 1}")
    label_device_id.pack(side=tk.LEFT)

    label_ip_address = tk.Label(frame_device, text="IP:")
    label_ip_address.pack(side=tk.LEFT)

    ip_entry = tk.Entry(frame_device)
    ip_entry.pack(side=tk.LEFT)
    
    label_port_number = tk.Label(frame_device, text="Port:")
    label_port_number.pack(side=tk.LEFT)

    port_entry = tk.Entry(frame_device)
    port_entry.pack(side=tk.LEFT)

    start_button_device = tk.Button(frame_device, text="Начать", command=lambda i=i: start_measurement(i))
    start_button_device.pack(side=tk.LEFT)

    stop_button_device = tk.Button(frame_device, text="Остановить", command=lambda i=i: stop_measurement(i))
    stop_button_device.pack(side=tk.LEFT)

    # Добавление квадрата вместо изображения весов 
    canvas_square_label= tk.Canvas(frame_device,width=50,height=50,bg='blue')
    canvas_square_label.pack(side=tk.LEFT)

    # Рисуем квадрат (весы) на Canvas 
    canvas_square_label.create_rectangle(5,5,45,45,outline='black', fill='blue')

    # Добавление полей ввода в списки для дальнейшего использования 
    ip_entries.append(ip_entry)
    port_entries.append(port_entry)

    frame_device.pack(pady=5)

# Запуск основного цикла приложения
root.mainloop()