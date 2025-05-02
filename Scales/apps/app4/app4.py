import socket
import struct
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import threading

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

def process_weight(last_weight, massa, measurement_count, filename, massa1, measurement_count1, filename1, massaw, measurement_count_weight):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    measurement_count_weight += 1
    massaw += last_weight 
    if 1000 <= last_weight <= 1020:
        massa += last_weight
        measurement_count += 1
        output_string = f"{current_time}\nЗамер {measurement_count} ({measurement_count_weight}): Масса нетто : {last_weight} г - Сумарный вес : {massa} г ({massaw} г)\n"
        write_to_file(filename, output_string)
        last_weight = 0
        return massa, measurement_count, last_weight, massa1, measurement_count1, massaw, measurement_count_weight

    else:  
        massa1 += last_weight
        measurement_count1 += 1
        output_string1 = f"{current_time}\nЗамер {measurement_count1} ({measurement_count_weight}): Масса нетто : {last_weight} г - Сумарный вес : {massa1} г ({massaw} г)\n"
        write_to_file(filename1, output_string1)
        last_weight = 0
        return massa, measurement_count, last_weight, massa1, measurement_count1, massaw, measurement_count_weight

class WeightApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Весы Приложение")

        self.text_area = scrolledtext.ScrolledText(self.root, width=60, height=20)
        self.text_area.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Включить", command=self.start_measurements_thread)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self.root, text="Выключить", command=self.stop_measurements)
        self.stop_button.pack(pady=5)

        self.filename_good = 'Good.txt'
        self.filename_bad = 'Bad.txt'
        
        self.measurement_count = 0  
        self.massa = 0
        self.measurement_count1 = 0 
        self.massa1 = 0
        self.measurement_count_weight = 0
        self.massaw = 0                 
        self.last_weight = 0      
        
        # Флаг для остановки потока замеров
        self.running = False

    def start_measurements_thread(self):
        if not self.running:  
            self.running = True  
            self.text_area.insert(tk.END, "Программа запущена\n")
            threading.Thread(target=self.start_measurements).start()

    def stop_measurements(self):
        if self.running:  
            self.running = False  
            self.text_area.insert(tk.END, "Ожидание завершения замеров...\n")

    def start_measurements(self):
        HOST = '192.168.1.94'  
        PORT = 5001            

        header = bytes([0xF8, 0x55, 0xCE])
        length = struct.pack('<H', 0x0001)  
        command = bytes([0x23])              

        message = header + length + command

        crc = calculate_crc(message[3:])  
        crc_bytes = struct.pack('<H', crc)

        full_message = message + crc_bytes
        
       # Основной цикл замеров.
       while True: 
            if not self.running: 
                break
            
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
                            attempts = 5  
                            while attempts > 0 and self.running:   
                                s.sendall(full_message)
                                data = s.recv(1024)
                                if data:
                                    set_weight_bytes = data[6:10]
                                    set_stable_byte = data[11]
                                    set_zero_byte = data[13]

                                    set_weight = struct.unpack('<I', set_weight_bytes)[0]

                                    if (800 <= set_weight <= 1200 and set_stable_byte == 1):
                                        if set_stable_byte == 1: 
                                            self.last_weight = set_weight

                                    if set_zero_byte == 1 or (0 <= set_weight <= 100) or set_weight > 10000:
                                        if self.last_weight != 0:
                                            (
                                                self.massa,
                                                self.measurement_count,
                                                self.last_weight,
                                                self.massa1,
                                                self.measurement_count1,
                                                self.massaw,
                                                self.measurement_count_weight,
                                            ) = process_weight(
                                                self.last_weight,
                                                self.massa,
                                                self.measurement_count,
                                                self.filename_good,
                                                self.massa1,
                                                self.measurement_count1,
                                                self.filename_bad,
                                                self.massaw,
                                                self.measurement_count_weight,
                                            )
                                            # Обновляем текстовое поле в главном потоке без всплывающих окон.
                                            output_message=(f"Замер завершен: {self.last_weight} г\n")
                                            # Используем метод insert для обновления текстового поля.
                                            # Обновляем текстовое поле в главном потоке
                                  
                                           break
        
                                attempts -= 1
                    
                    else:
                        output_message="Ответ не получен.\n"
                        print(output_message)
                        break
                
                except socket.timeout:
                    output_message="Время ожидания ответа истекло.\n"
                    print(output_message)
                except Exception as e:
                    output_message=f"Ошибка: {str(e)}\n"
                    print(output_message)

if __name__ == "__main__":
    app=WeightApp()
    app.root.mainloop()