import pathlib
import aiosqlite
from datetime import datetime

dir_path = pathlib.Path.cwd()
path = pathlib.Path(dir_path, 'db', 'crypto_analisys.db')


# Асинхронная функция для записи данных пользователя
async def write_user(chat_id: int, username: str, first_name: str, last_name: str, language: str, interval: str) -> None:
    async with aiosqlite.connect(path) as conn:
        async with conn.cursor() as c:
            await c.execute('''
                INSERT INTO user (chat_id, username, first_name, last_name, language, interval)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    language=excluded.language,
                    interval=excluded.interval
            ''', (chat_id, username, first_name, last_name, language, interval))
            await conn.commit()


# Асинхронная функция для записи запроса пользователя
async def user_request(chat_id: int, interval: str, trading_pair: str, time: str) -> None:
    async with aiosqlite.connect(path) as conn:
        async with conn.cursor() as c:
            await c.execute('''
                INSERT INTO request (chat_id, interval, trading_pair, time)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, interval, trading_pair, time))
            await conn.commit()
