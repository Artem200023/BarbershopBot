import socket
import struct
import asyncio
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import pandas as pd
import openpyxl
import os
from excel_formatter import format_excel, append_to_excel
from sqlite_manager import SQLiteManager

class ScaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Весы")
        self.root.geometry("1000x700")
        self._export_running = False
        
        # Новые переменные для управления подключениями
        self.active_devices = set()  # Множество для отслеживания активных устройств
        self.device_tasks = {}       # Словарь для хранения задач по устройствам
        
        # Установка иконки
        try:
            icon_path = "logo.ico"
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")
        
        # Главный фрейм (без изменений)
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Фрейм для устройств (левая панель) (без изменений)
        self.devices_frame = tk.Frame(self.main_frame, width=250, relief=tk.RAISED, borderwidth=1)
        self.devices_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.devices_frame.pack_propagate(False)
        
        # Фрейм для добавления нового устройства (без изменений)
        self.add_device_frame = tk.LabelFrame(self.devices_frame, text="Добавить весы", padx=5, pady=5)
        self.add_device_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Поля ввода (без изменений)
        tk.Label(self.add_device_frame, text="ID весов:").pack(anchor=tk.W)
        self.id_entry = tk.Entry(self.add_device_frame)
        self.id_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(self.add_device_frame, text="IP адрес:").pack(anchor=tk.W)
        self.ip_entry = tk.Entry(self.add_device_frame)
        self.ip_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(self.add_device_frame, text="Порт:").pack(anchor=tk.W)
        self.port_entry = tk.Entry(self.add_device_frame)
        self.port_entry.pack(fill=tk.X, pady=(0, 10))
        self.port_entry.insert(0, "5001")
        
        self.add_button = tk.Button(self.add_device_frame, text="Добавить", command=self.add_device)
        self.add_button.pack(fill=tk.X)
        
        # Список устройств с прокруткой (с добавлением привязки события)
        self.devices_list_frame = tk.Frame(self.devices_frame)
        self.devices_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.devices_listbox = tk.Listbox(self.devices_list_frame)
        self.devices_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.devices_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.devices_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.devices_listbox.yview)
        
        # Привязка события выбора устройства (НОВОЕ)
        self.devices_listbox.bind('<<ListboxSelect>>', self.on_device_select)
        
        # Фрейм для управления (правая часть) (без изменений)
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Текстовая область (без изменений)
        self.text_area = scrolledtext.ScrolledText(self.control_frame, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для кнопок управления (без изменений)
        self.button_frame = tk.Frame(self.control_frame)
        self.button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.start_button = tk.Button(self.button_frame, text="Начать измерение (1 весы)", 
                                    command=self.start_single_measurement)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.parallel_button = tk.Button(self.button_frame, text="Начать все измерения", 
                                       command=self.start_parallel_measurement)
        self.parallel_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.stop_button = tk.Button(self.button_frame, text="Остановить все", 
                                   command=self.stop_measurement)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Новая кнопка для остановки выбранных весов
        self.stop_single_button = tk.Button(self.button_frame, 
                                          text="Остановить выбранные весы",
                                          command=self.stop_single_measurement)
        self.stop_single_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Кнопка экспорта в Excel (без изменений)
        self.export_button = tk.Button(self.button_frame, text="Экспорт в Excel",
                                     command=self._start_export)
        self.export_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # НОВАЯ кнопка для показа всех весов
        self.show_all_btn = tk.Button(self.button_frame, 
                                    text="Показать все весы",
                                    command=self.show_all_devices)
        self.show_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Инициализация переменных (с небольшими изменениями)
        self.reset_measurements()
        self.devices = []
        self.active_tasks = []
        self.stop_measurement_flag = False
        self.connected_successfully = False
        self.sync_lock = threading.Lock()
        
        # Для управления отображением (НОВОЕ)
        self.show_all_messages = True
        self.current_device_filter = None
        self.global_message_buffer = []
        self.max_buffer_size = 1000  # Максимальное количество хранимых сообщений
        
        # Инициализация менеджеров (без изменений)
        self.sqlite_manager = SQLiteManager()
        self.excel_formatter = type('ExcelFormatter', (), {
            'format_excel': format_excel,
            'append_to_excel': append_to_excel
        })

        self.devices = self.sqlite_manager.get_all_scales()  # Загружаем весы из БД
        self.update_devices_listbox()  # Обновляем список сразу
        self.remove_button = tk.Button(self.add_device_frame, 
                             text="Удалить выбранные",
                             command=self.remove_device)
        self.remove_button.pack(fill=tk.X, pady=5)

    # НОВЫЙ метод: обработка выбора устройства в списке
    def on_device_select(self, event):
        """Обработка выбора весов - для отображения данных"""
        selection = self.devices_listbox.curselection()
        if selection:
            selected_device = self.devices[selection[0]]
            self.current_device_filter = selected_device['id']
            self.show_all_messages = False
            self.refresh_display()

    # НОВЫЙ метод: показ всех устройств
    def show_all_devices(self):
        """Возврат к отображению всех весов"""
        self.show_all_messages = True
        self.current_device_filter = None
        self.refresh_display()

    # НОВЫЙ метод: обновление отображения
    def refresh_display(self):
        """Обновление отображения с учетом текущих фильтров"""
        self.text_area.delete(1.0, tk.END)
        
        # Добавляем заголовок с текущим режимом
        if self.show_all_messages:
            mode_text = "=== Режим: Все весы ==="
        else:
            mode_text = f"=== Режим: Весы {self.current_device_filter} ==="
        
        self.text_area.insert(tk.END, f"{mode_text}\n\n")
        
        # Выводим сообщения
        for device_id, message in self.global_message_buffer:
            if self.show_all_messages or device_id == self.current_device_filter:
                self.text_area.insert(tk.END, message)
        
        self.text_area.see(tk.END)

    # НОВЫЙ метод: обновление списка устройств с индикацией статуса
    def update_devices_listbox(self):
        """Обновление списка устройств с отображением статуса"""
        self.devices_listbox.delete(0, tk.END)
        for device in self.devices:
            status = "ON" if device['id'] in self.active_devices else "OFF"
            color = 'green' if device['id'] in self.active_devices else 'red'
            self.devices_listbox.insert(tk.END, 
                                     f"{device['id']} ({device['ip']}:{device['port']}) [{status}]")
            self.devices_listbox.itemconfig(tk.END, {'fg': color})

    # Измененный метод: добавление устройства с проверкой на дубликаты
    def add_device(self):
        device_id = self.id_entry.get()
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        
        if device_id and ip and port:
            try:
                port = int(port)
                # Проверка на дубликаты (НОВОЕ)
                if any(d['id'] == device_id for d in self.devices):
                    self.log(f"Ошибка: весы {device_id} уже добавлены")
                    return

                # Сохраняем в SQLite
                self.sqlite_manager.add_scale(device_id, ip, port)

                # Обновляем локальный список
                self.devices = self.sqlite_manager.get_all_scales()
                self.update_devices_listbox()

                self.id_entry.delete(0, tk.END)
                self.ip_entry.delete(0, tk.END)
                self.port_entry.delete(0, tk.END)
                self.port_entry.insert(0, "5001")

                      
            except ValueError:
                self.log("Ошибка: порт должен быть числом")

    def remove_device(self):
        """Удаление выбранных весов"""
        selection = self.devices_listbox.curselection()
        if not selection:
            self.log("Ошибка: не выбраны весы для удаления")
            return
        
        device = self.devices[selection[0]]
    
        # Удаляем из БД
        self.sqlite_manager.remove_scale(device['id'])
    
        # Обновляем список
        self.devices = self.sqlite_manager.get_all_scales()
        self.update_devices_listbox()
        self.log(f"Весы {device['id']} удалены")

    # Измененный метод: логирование с учетом фильтров
    def log(self, message, device_id=None):
        """Логирование с учетом фильтров"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        full_message = f"{timestamp} - {message}\n"
        
        # Сохраняем сообщение в буфер (удаляем старые при необходимости)
        self.global_message_buffer.append((device_id, full_message))
        if len(self.global_message_buffer) > self.max_buffer_size:
            self.global_message_buffer.pop(0)
        
        # Выводим только если:
        # 1. Режим "все весы" ИЛИ 
        # 2. Это сообщение от текущего выбранного устройства
        if self.show_all_messages or device_id == self.current_device_filter:
            self.text_area.insert(tk.END, full_message)
            self.text_area.see(tk.END)

    # Измененный метод: запуск измерения для одного устройства
    def start_single_measurement(self):
        """Запуск измерения для выбранного устройства"""
        selection = self.devices_listbox.curselection()
        if not selection:
            self.log("Ошибка: не выбраны весы для измерения")
            return
            
        device = self.devices[selection[0]]
        
        # Проверяем, не запущено ли уже измерение (НОВОЕ)
        if device['id'] in self.active_devices:
            self.log(f"Измерение для {device['id']} уже запущено")
            return
            
        self.stop_measurement_flag = False
        self.active_devices.add(device['id'])
        self.update_devices_listbox()  # Обновляем статус в списке
        task = asyncio.create_task(self.measure_single_device(device))
        self.active_tasks.append(task)

    # Измененный метод: параллельный запуск измерений
    def start_parallel_measurement(self):
        """Запуск параллельных измерений для всех устройств"""
        if not self.devices:
            self.log("Ошибка: не добавлены весы для измерения")
            return
            
        self.stop_measurement_flag = False
        for device in self.devices:
            if device['id'] not in self.active_devices:  # НОВОЕ: проверка активности
                self.active_devices.add(device['id'])
                task = asyncio.create_task(self.measure_single_device(device))
                self.active_tasks.append(task)
        self.update_devices_listbox()  # Обновляем статусы в списке

    # Измененный метод: остановка измерений
    def stop_measurement(self):
        """Остановка всех измерений"""
        self.stop_measurement_flag = True
        self.active_devices.clear()  # НОВОЕ: очищаем активные устройства
        self.update_devices_listbox()  # Обновляем статусы в списке
        self.log("Измерения остановлены")

    # Новый метод: остановка выбранного устройства
    def stop_single_measurement(self):
        """Остановка только выбранного устройства"""
        selection = self.devices_listbox.curselection()
        if not selection:
            self.log("Ошибка: не выбраны весы для остановки")
            return
            
        device = self.devices[selection[0]]
        
        if device['id'] not in self.active_devices:
            self.log(f"Весы {device['id']} уже остановлены")
            return
        
        self.active_devices.remove(device['id'])
        self.update_devices_listbox()
        self.log(f"Измерение для весов {device['id']} остановлено")

    # Измененный метод: измерение для одного устройства
    async def measure_single_device(self, device):
        """Измерение для одного устройства с автоматическим переподключением"""
        try:
            # Помечаем устройство как активное (НОВОЕ)
            self.active_devices.add(device['id'])
            self.update_devices_listbox()
            
            header = bytes([0xF8, 0x55, 0xCE])
            length = struct.pack('<H', 0x0001)
            command = bytes([0x23])
            message = header + length + command
            crc = self.calculate_crc(message[3:])  
            full_message = message + struct.pack('<H', crc)

            current_stable_weight = None

            while device['id'] in self.active_devices:
                try:
                    reader, writer = await asyncio.open_connection(device['ip'], device['port'])
                    self.log(f"Подключено к {device['id']} ({device['ip']}:{device['port']})", device['id'])

                    try:
                        while device['id'] in self.active_devices:
                            writer.write(full_message)
                            await writer.drain()

                            try:
                                data = await asyncio.wait_for(reader.read(1024), timeout=3.0)
                                if len(data) >= 14:
                                    set_weight_bytes = data[6:10]
                                    set_stable_byte = data[11]
                                    set_zero_byte = data[13]
                                    current_weight = struct.unpack('<I', set_weight_bytes)[0]

                                    if set_stable_byte == 1 and 800 <= current_weight <= 1200:
                                        current_stable_weight = current_weight
                                    elif current_weight < 100 or set_zero_byte == 1:
                                        if current_stable_weight is not None:
                                            self.process_weight(device['id'], current_stable_weight)
                                            current_stable_weight = None
                                else:
                                    break
                            except (struct.error, IndexError):
                                continue

                            await asyncio.sleep(0.1)

                    except (ConnectionError, TimeoutError, asyncio.TimeoutError) as e:
                        self.log(f"Ошибка связи с {device['id']}: {e}. Переподключение...", device['id'])
                
                    finally:
                        writer.close()
                        await writer.wait_closed()

                except (ConnectionError, OSError) as e:
                    self.log(f"Не удалось подключиться к {device['id']}: {e}. Повтор через 3 сек...", device['id'])
                    await asyncio.sleep(3)
        finally:
            # По завершении измерения убираем из активных (НОВОЕ)
            if device['id'] in self.active_devices:
                self.active_devices.remove(device['id'])
            self.update_devices_listbox()

    # Остальные методы без изменений:
    def _start_export(self):
        """Запуск процесса экспорта"""
        if self._export_running:
            return
            
        self._export_running = True
        self.export_button.config(state=tk.DISABLED, text="Экспорт...")
        
        # Создаем модальное окно прогресса
        self.export_progress = tk.Toplevel(self.root)
        self.export_progress.title("Экспорт данных")
        self.export_progress.geometry("300x100")
        self.export_progress.grab_set()
        self.export_progress.protocol("WM_DELETE_WINDOW", lambda: None)
        
        tk.Label(self.export_progress, text="Идет экспорт данных...").pack(pady=10)
        self.progress_bar = ttk.Progressbar(self.export_progress, mode='indeterminate')
        self.progress_bar.pack(pady=5)
        self.progress_bar.start()
        
        # Запускаем экспорт через asyncio
        asyncio.create_task(self._run_export_async())

    async def _run_export_async(self):
        """Асинхронная задача экспорта данных"""
        try:
            # Получаем данные из SQLite
            devices_data = self.sqlite_manager.get_devices_data()
        
            # Создаем временный файл
            temp_filename = "temp_export.xlsx"
        
            # Создаем Excel writer один раз
            with pd.ExcelWriter(temp_filename, engine='openpyxl') as writer:
                # Собираем список всех листов для последующего форматирования
                sheet_names = []
            
                for device_id, df in devices_data.items():
                    # Форматируем данные
                    result_df = pd.DataFrame({
                        'Дата': df['date'],
                        'Время': df['time'],
                        'Вес норма (г)': df.apply(lambda x: x['weight'] if x['status'] == 'норма' else 0, axis=1),
                        'Замер норма': df.apply(lambda x: 1 if x['status'] == 'норма' else 0, axis=1),
                        'Вес не норма (г)': df.apply(lambda x: x['weight'] if x['status'] != 'норма' else 0, axis=1),
                        'Замер не норма': df.apply(lambda x: 1 if x['status'] != 'норма' else 0, axis=1),
                        'Кол-во замеров': df['total_count'],
                        'Весь суммарный вес (г)': df['total_weight'],
                        'Суммарный вес норма (г)': df['good_weight'],
                        'Суммарный вес не норма (г)': df['bad_weight']
                    })
                
                    sheet_name = f"Весы {device_id}"
                    sheet_names.append(sheet_name)
                    result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
            # Применяем форматирование ко всем листам
            self.excel_formatter.format_excel(temp_filename, sheet_names=sheet_names)
        
            # Заменяем основной файл
            final_filename = "Datas.xlsx"
            if os.path.exists(final_filename):
                os.remove(final_filename)
            os.rename(temp_filename, final_filename)
        
            # Успешное завершение
            self._finish_export(True, "Данные успешно экспортированы в Excel!")
        
        except Exception as e:
            # Ошибка экспорта
            self._finish_export(False, f"Ошибка экспорта: {str(e)}")
            if os.path.exists("temp_export.xlsx"):
                os.remove("temp_export.xlsx")
        
        finally:
            self._export_running = False

    def _finish_export(self, success, message):
        """Завершение экспорта и обновление GUI"""
        if not self.root.winfo_exists():
            return
            
        try:
            # Останавливаем прогресс-бар
            if hasattr(self, 'progress_bar'):
                self.progress_bar.stop()
            
            # Закрываем окно прогресса
            if hasattr(self, 'export_progress'):
                self.export_progress.grab_release()
                self.export_progress.destroy()
            
            # Показываем сообщение
            if success:
                messagebox.showinfo("Успех", message)
            else:
                messagebox.showerror("Ошибка", message)
            
            # Восстанавливаем кнопку
            if hasattr(self, 'export_button'):
                self.export_button.config(state=tk.NORMAL, text="Экспорт в Excel")
                
        except Exception as e:
            print(f"Ошибка при завершении экспорта: {e}")

    def reset_measurements(self):
        self.measurement_data = {
            'total_count': 0,
            'good_count': 0,
            'bad_count': 0,
            'total_weight': 0,
            'good_weight': 0,
            'bad_weight': 0,
        }

    def process_weight(self, device_id, weight):
        """Обработка результатов измерения"""
        current_time = datetime.now()
        is_good = 1000 <= weight <= 1020
        
        with self.sync_lock:
            self.measurement_data['total_count'] += 1
            self.measurement_data['total_weight'] += weight
            
            if is_good:
                self.measurement_data['good_count'] += 1
                self.measurement_data['good_weight'] += weight
                status = "норма"
            else:
                self.measurement_data['bad_count'] += 1
                self.measurement_data['bad_weight'] += weight
                status = "не норма"
        
        output = (f"Измерение: {weight}г ({status})\n"
                 f"Всего: {self.measurement_data['total_count']} замеров, "
                 f"Суммарный вес: {self.measurement_data['total_weight']}г\n")
        self.log(output, device_id)
        
        # Записываем в SQLite
        self.sqlite_manager.add_measurement({
            'Дата': current_time.strftime('%d-%m-%Y'),
            'Время': current_time.strftime('%H:%M:%S'),
            'ID весов': device_id,
            'Вес (г)': weight,
            'Статус': status,
            'Кол-во замеров': self.measurement_data['total_count'],
            'Весь суммарный вес (г)': self.measurement_data['total_weight'],
            'Суммарный вес норма (г)': self.measurement_data['good_weight'],
            'Суммарный вес не норма (г)': self.measurement_data['bad_weight']
        })

    def calculate_crc(self, data):
        """Вычисление CRC"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if (crc & 0x0001) != 0:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def run(self):
        async def run_tk():
            while True:
                try:
                    self.root.update()
                    await asyncio.sleep(0.05)
                except tk.TclError:
                    self.stop_measurement()
                    break

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_tk())
        finally:
            self.sqlite_manager.close()
            loop.close()

def main():
    root = tk.Tk()
    app = ScaleApp(root)
    app.run()

if __name__ == "__main__":
    main()

# pyinstaller --onefile --windowed --icon=D:\\Python\\Application\\app4\\logo.ico app4.py