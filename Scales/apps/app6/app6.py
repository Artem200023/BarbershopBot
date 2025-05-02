import socket
import struct
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading

# Глобальная переменная для остановки потока измерений
stop_measurement_flag = False

class WeightMeasurement:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.stop_flag = False  # Флаг остановки для каждого устройства
        self.measurement_count = 0
        self.massa = 0
        self.last_weight = 0

    def calculate_crc(self, data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if (crc & 0x0001) != 0:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def write_to_file(self, filename, data):
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(data + '\n')

    def start_measurement(self):
        self.stop_flag = False  # Сброс флага остановки
        threading.Thread(target=self.measure).start()

    def stop_measurement(self):
        self.stop_flag = True  # Установка флага остановки

    def measure(self):
        header = bytes([0xF8, 0x55, 0xCE])
        length = struct.pack('<H', 0x0001)
        command = bytes([0x23])
        
        message = header + length + command
        crc = self.calculate_crc(message[3:])
        crc_bytes = struct.pack('<H', crc)
        full_message = message + crc_bytes

        filename = 'Datas.txt'
        
        connected_successfully = False  # Флаг успешного подключения

        while not self.stop_flag:  # Проверка флага остановки в цикле
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((self.host, self.port))
                    if not connected_successfully:  
                        text_area.insert(tk.END, f"Подключение к {self.host} успешно.\n")
                        connected_successfully = True
                    
                    s.sendall(full_message)

                    s.settimeout(10)
                    data = s.recv(1024)

                    if data:
                        set_weight_bytes = data[6:10]
                        set_stable_byte = data[11]
                        set_zero_byte = data[13]

                        if set_zero_byte != 1:
                            while not self.stop_flag:  
                                s.sendall(full_message)
                                data = s.recv(1024)
                                if data:
                                    set_weight_bytes = data[6:10]
                                    set_stable_byte = data[11]
                                    set_zero_byte = data[13]

                                    set_weight = struct.unpack('<I', set_weight_bytes)[0]

                                    if 800 <= set_weight <= 1200 and set_stable_byte == 1:
                                        self.last_weight = set_weight

                                    if set_zero_byte == 1 or (self.last_weight >= set_weight + 750) or set_weight > 10000:
                                        if self.last_weight != 0:
                                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            self.massa += self.last_weight
                                            self.measurement_count += 1
                                            output_string = f"{current_time}\nЗамер {self.measurement_count}: Масса нетто : {self.last_weight} г - Сумарный вес : {self.massa} г\n"
                                            
                                            # Обновление текстового поля в основном потоке GUI
                                            text_area.insert(tk.END, output_string)
                                            self.write_to_file(filename, output_string)
                                            self.last_weight = 0
                                            break

                except socket.timeout:
                    if connected_successfully: 
                        text_area.insert(tk.END, f"Время ожидания ответа от {self.host} истекло.\n")
                except Exception as e:
                    text_area.insert(tk.END, f"Ошибка с {self.host}: {e}\n")
                    connected_successfully = False


# Создание основного окна приложения
root = tk.Tk()
root.title("Весы")

# Создание текстового поля для вывода данных
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
text_area.pack(padx=10, pady=10)

# Поля для ввода IP и порта весов
ip_label = tk.Label(root, text="IP адрес:")
ip_label.pack(pady=5)

ip_entry = tk.Entry(root)
ip_entry.pack(pady=5)

port_label = tk.Label(root, text="Порт:")
port_label.pack(pady=5)

port_entry = tk.Entry(root)
port_entry.pack(pady=5)

weights_list = []  # Список весов

# Кнопка для добавления нового устройства в список весов
def add_device():
    ip_address = ip_entry.get()
    port_number_str = port_entry.get()
    
    try:
        port_number = int(port_number_str)
        
        if not (1 <= port_number <= 65535):
            raise ValueError("Порт должен быть в диапазоне от 1 до 65535.")
        
        weight_device = WeightMeasurement(ip_address, port_number)
        weights_list.append(weight_device)
        
        text_area.insert(tk.END, f"Устройство добавлено: {ip_address}:{port_number}\n")
        
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))

add_button = tk.Button(root, text="Добавить устройство", command=add_device)
add_button.pack(pady=5)

# Кнопка для начала измерений для всех весов
def start_all_measurements():
    for weight in weights_list:
        weight.start_measurement()

start_button = tk.Button(root, text="Начать измерение", command=start_all_measurements)
start_button.pack(pady=5)

# Кнопка для остановки измерений для всех весов
def stop_all_measurements():
    for weight in weights_list:
        weight.stop_measurement()

stop_button = tk.Button(root, text="Остановить измерение", command=stop_all_measurements)
stop_button.pack(pady=5)

# Запуск основного цикла приложения
root.mainloop()