import pathlib
import sqlite3
from datetime import datetime

# Определение пути к базе данных
dir_path = pathlib.Path.cwd()
path = pathlib.Path(dir_path, 'crypto_analisys.db')
print(path)


# Функция для создания базы данных и таблиц
def create_db() -> None:
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT,
                interval TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                interval TEXT,
                trading_pair TEXT,
                time TEXT
            )
        ''')
        conn.commit()


create_db()
