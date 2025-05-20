import sqlite3
import threading
import pandas as pd 

class SQLiteManager:
    def __init__(self, db_name='scales_data.db'):
        self.db_conn = sqlite3.connect(db_name, check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        with self.lock:
            self.db_conn.execute('''CREATE TABLE IF NOT EXISTS measurements
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 date TEXT, time TEXT, device_id TEXT,
                                 weight REAL, status TEXT,
                                 total_count INTEGER, total_weight REAL,
                                 good_weight REAL, bad_weight REAL)''')
            self.db_conn.commit()

    def add_measurement(self, data):
        with self.lock:
            try:
                self.db_conn.execute('''INSERT INTO measurements 
                                    (date, time, device_id, weight, status,
                                     total_count, total_weight, 
                                     good_weight, bad_weight)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                    (data['Дата'], data['Время'], data['ID весов'],
                                     data['Вес (г)'], data['Статус'],
                                     data['Кол-во замеров'], data['Весь суммарный вес (г)'],
                                     data['Суммарный вес норма (г)'], data['Суммарный вес не норма (г)']))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка записи в БД: {e}")
                return False

    def get_devices_data(self):
        with self.lock:
            devices = self.db_conn.execute("SELECT DISTINCT device_id FROM measurements").fetchall()
            result = {}
            for device in devices:
                device_id = device[0]
                query = f"SELECT * FROM measurements WHERE device_id = '{device_id}' ORDER BY date, time"
                df = pd.read_sql_query(query, self.db_conn)
                result[device_id] = df
            return result

    def close(self):
        self.db_conn.close()