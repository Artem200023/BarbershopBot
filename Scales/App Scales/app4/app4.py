import socket
import struct
import asyncio
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import pandas as pd
import openpyxl
from excel_formatter import format_excel, append_to_excel

# Глобальная переменная для остановки измерений
stop_measurement_flag = False

class ScaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Весы")
        
        # Установка иконки
        icon_path = "D:\\Python\\Application\\scales\\logo.ico"
        self.root.iconbitmap(icon_path)
        
        # Создание интерфейса
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10)
        
        self.start_button = tk.Button(root, text="Начать измерение", command=self.start_measurement)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(root, text="Остановить измерение", command=self.stop_measurement)
        self.stop_button.pack(pady=5)
        
        # Инициализация переменных
        self.measurement_count = 0
        self.massa = 0
        self.good_last_weight = 0
        self.measurement_count1 = 0
        self.massa1 = 0
        self.measurement_count_weight = 0
        self.massaw = 0
        self.bad_last_weight = 0
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

    def process_weight(self):
        current_time_date = datetime.now().strftime("%Y-%m-%d")
        current_time_time = datetime.now().strftime("%H:%M:%S")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.measurement_count_weight += 1
        self.massaw += self.last_weight
        filename_excel = 'Datas.xlsx'

        if 1000 <= self.last_weight <= 1020:
            self.massa += self.last_weight
            self.measurement_count += 1
            self.good_last_weight = self.last_weight
            output_string = f"{current_time}\nЗамер {self.measurement_count} ({self.measurement_count_weight}): Масса нетто : {self.last_weight} г - Суммарный вес : {self.massa} г ({self.massaw} г)\n"
        else:  
            self.massa1 += self.last_weight
            self.measurement_count1 += 1
            self.bad_last_weight = self.last_weight
            output_string = f"{current_time}\nЗамер {self.measurement_count1} ({self.measurement_count_weight}): Масса нетто : {self.last_weight} г - Суммарный вес : {self.massa1} г ({self.massaw} г)\n"
        
        self.text_area.insert(tk.END, output_string)

        # Запись данных в Excel
        append_to_excel(filename_excel, {
            'Дата': current_time_date,
            'Время': current_time_time,
            'Замер норма': self.measurement_count if self.good_last_weight > 0 else 0,   
            'Вес норма (г)': self.good_last_weight,
            'Замер не норма': self.measurement_count1 if self.bad_last_weight > 0 else 0,
            'Вес не норма (г)': self.bad_last_weight,
            'Кол-во замеров': self.measurement_count_weight,
            'Весь суммарный вес (г)': self.massaw,
            'Суммарный вес норма (г)': self.massa,
            'Суммарный вес не норма (г)': self.massa1,
        })
        
        self.last_weight = 0
        self.good_last_weight = 0
        self.bad_last_weight = 0

    async def measure(self):
        HOST = '192.168.1.94'
        PORT = 5001
        
        # Формирование сообщения для запроса массы
        header = bytes([0xF8, 0x55, 0xCE])
        length = struct.pack('<H', 0x0001)
        command = bytes([0x23])
        message = header + length + command
        crc = self.calculate_crc(message[3:])  
        crc_bytes = struct.pack('<H', crc)
        full_message = message + crc_bytes

        # Команда установки 0
        command_reset_zero = bytes([0x72])   
        message_reset_zero = header + length + command_reset_zero
        crc_reset_zero = self.calculate_crc(message_reset_zero[3:])  
        crc_bytes_reset_zero = struct.pack('<H', crc_reset_zero)
        full_message_reset_zero = message_reset_zero + crc_bytes_reset_zero

        connected_successfully = False

        while not stop_measurement_flag:
            try:
                reader, writer = await asyncio.open_connection(HOST, PORT)
                
                if not connected_successfully:
                    self.text_area.insert(tk.END, "Подключение успешно.\n")
                    connected_successfully = True

                writer.write(full_message)
                await writer.drain()

                data = await asyncio.wait_for(reader.read(1024), timeout=10)

                if data:
                    set_weight_bytes = data[6:10]   
                    set_stable_byte = data[11]      
                    set_zero_byte = data[13]        

                    if set_zero_byte != 1:
                        while not stop_measurement_flag:    
                            writer.write(full_message)
                            await writer.drain()
                            
                            data = await asyncio.wait_for(reader.read(1024), timeout=10)
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
                                        self.process_weight()
                                        break
                                    else:
                                        break

            except asyncio.TimeoutError:
                if connected_successfully:
                    self.text_area.insert(tk.END, "Время ожидания ответа истекло.\n")
            except Exception as e:
                self.text_area.insert(tk.END, f"Ошибка: {e}\n")
                connected_successfully = False
            finally:
                if 'writer' in locals():
                    writer.close()
                    await writer.wait_closed()

    def start_measurement(self):
        global stop_measurement_flag
        stop_measurement_flag = False
        asyncio.create_task(self.run_measurement())

    async def run_measurement(self):
        await self.measure()

    def stop_measurement(self):
        global stop_measurement_flag
        stop_measurement_flag = True

def main():
    root = tk.Tk()
    app = ScaleApp(root)
    
    loop = asyncio.get_event_loop()
    
    def close_window():
        global stop_measurement_flag
        stop_measurement_flag = True
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", close_window)
    
    async def run_tk():
        while not stop_measurement_flag:
            root.update()
            await asyncio.sleep(0.05)
    
    loop.run_until_complete(run_tk())
    loop.close()

if __name__ == "__main__":
    main()