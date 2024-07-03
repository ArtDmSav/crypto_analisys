from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base

from db.db_create import Operations

DATABASE_URL = "postgresql+asyncpg://admin:password@localhost/crypto"

# Создаем движок базы данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем базовый класс для объявлений моделей
Base = declarative_base()


# Определяем модель для таблицы user
class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(30), nullable=False)
    registration_datetime = sa.Column(sa.DateTime, nullable=False)
    status = sa.Column(sa.Integer, default=1)
    last_activity_datetime = sa.Column(sa.DateTime)
    language = sa.Column(sa.String(5))
    account_id = sa.Column(sa.Integer, default=0)
    update_status = sa.Column(sa.Boolean, nullable=False, default=False)
    update_interval = sa.Column(sa.Integer, nullable=False, default=0)
    update_time = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    interval = sa.Column(sa.String(5), nullable=False, default="1h")
    trading_pair = sa.Column(sa.String(10), nullable=False, default="BTCUSDT")
    chat_id = sa.Column(sa.BigInteger, default=0)


# Создаем асинхронную сессию
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def add_user(username: str,
                   language='xz',
                   registration_datetime=datetime.now(),
                   last_activity_datetime=datetime.now()) -> int:
    try:
        async with async_session() as session:
            async with session.begin():
                # Проверяем, существует ли пользователь с таким же именем
                query = select(User).where(User.username == username)
                result = await session.execute(query)
                user = result.scalars().first()

                if user:
                    # Обновляем статус пользователя
                    user.status = 1
                    await session.commit()
                    return 2

                # Добавляем нового пользователя
                new_user = User(
                    username=username,
                    registration_datetime=registration_datetime,
                    last_activity_datetime=last_activity_datetime,
                    language=language
                )
                session.add(new_user)
                await session.commit()
                return 1
    except Exception as e:
        return 0


async def update_pair() -> list:
    async with async_session() as session:
        async with session.begin():
            # Поиск пользователей с update_status == True
            query = select(User).where(User.update_status == True)
            result = await session.execute(query)
            users = result.scalars().all()

            if not users:
                return []

            # Форматирование данных в виде списка словарей
            users_info = [
                {
                    "chat_id": user.chat_id,
                    "trading_pair": user.trading_pair,
                    "interval": user.interval,
                    "update_time": user.update_time,
                    "update_interval": user.update_interval,
                    "language": user.language
                }
                for user in users
            ]
            print(users_info)
            return users_info


async def update_status(username: str, status: bool, update_interval: int = 86400) -> None:
    async with async_session() as session:
        async with session.begin():
            # Поиск пользователя по username
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalars().first()

            if user is None:
                print(f"User with username {username} not found.")
                return

            # Обновление полtq
            user.update_status = status
            user.update_interval = update_interval
            session.add(user)
            await session.commit()


async def update_update_time(chat_id: int, update_time: datetime) -> None:
    async with async_session() as session:
        async with session.begin():
            # Поиск пользователя по username
            query = select(User).where(User.chat_id == chat_id)
            result = await session.execute(query)
            user = result.scalars().first()

            if user is None:
                print(f"User with username {chat_id} not found.")
                return

            # Обновление поле
            user.update_time = update_time
            session.add(user)
            await session.commit()


async def check_user_exists(username: str) -> bool:
    async with async_session() as session:
        async with session.begin():
            query = select(User).where(User.username == username, User.status == 1)
            result = await session.execute(query)
            user = result.scalars().first()

            return user is not None


async def deactivate_user(username: str) -> int:
    async with async_session() as session:
        async with session.begin():
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalars().first()

            if user:
                await session.execute(
                    update(User)
                    .where(User.username == username)
                    .values(status=0)
                )
                await session.commit()
                return 1
            else:
                return 0


async def write_transaction(username: str,
                            interval: str,
                            trading_pair: str,
                            price: str,
                            lang_code: str,
                            chat_id: int = 0,
                            datatime=datetime.now()
                            ) -> None:
    print(f"\n\nwrite_transaction\nchat_id = {chat_id}\n\n")
    try:
        async with async_session() as session:
            async with session.begin():
                # Поиск пользователя по username
                query = select(User).where(User.username == username)
                result = await session.execute(query)
                user = result.scalars().first()

                if user is None:
                    print(f"User with username {username} not found.")
                    return

                # Обновление поля у пользователя
                user.last_activity_datetime = datatime
                user.language = lang_code
                user.interval = interval
                user.trading_pair = trading_pair
                user.update_time = datatime
                user.chat_id = chat_id

                session.add(user)

                # Создание новой операции
                new_operation = Operations(
                    user_id=user.id,
                    datetime=datatime,
                    interval=interval,
                    trading_pair=trading_pair,
                    price=price
                )
                session.add(new_operation)
                await session.commit()
                print(f"Transaction for user {username} added successfully.")
    except Exception as e:
        print(e)


async def get_user_info(username: str) -> str:
    try:
        async with async_session() as session:
            async with session.begin():
                # Поиск пользователя по userid
                query = select(User).where(User.username == username)
                result = await session.execute(query)
                user = result.scalars().first()

                if user is None:
                    return f"User with ID {username} not found."

                # Форматирование данных пользователя в строку
                user_info = (
                    f"User ID: {user.id}\n"
                    f"Username: {user.username}\n"
                    f"Registration DateTime: {user.registration_datetime}\n"
                    f"Status: {user.status}\n"
                    f"Last Activity DateTime: {user.last_activity_datetime}\n"
                    f"Language: {user.language}\n"
                )

                return user_info
    except Exception as e:
        return ''


async def get_last_10_transactions(username: str) -> str:
    try:
        async with async_session() as session:
            async with session.begin():
                # Поиск пользователя по username
                query = select(User).where(User.username == username)
                result = await session.execute(query)
                user = result.scalars().first()

                if user is None:
                    return f"User with username {username} not found."

                # Поиск последних 10 транзакций пользователя
                query = (
                    select(Operations)
                    .where(Operations.user_id == user.id)
                    .order_by(Operations.datetime.desc())
                    .limit(10)
                )
                result = await session.execute(query)
                transactions = result.scalars().all()

                if not transactions:
                    return f"No transactions found for user {username}."

                # Форматирование данных транзакций в строку
                transactions_info = "\n".join(
                    [
                        f"Transaction {i + 1}:\n"
                        f"  DateTime: {txn.datetime}\n"
                        f"  Interval: {txn.interval}\n"
                        f"  Trading Pair: {txn.trading_pair}\n"
                        f"  Price: {txn.price}\n"
                        for i, txn in enumerate(transactions)
                    ]
                )

                return transactions_info
    except Exception as e:
        print(e)
        return ''


async def get_user_list() -> str:
    try:
        async with async_session() as session:
            async with session.begin():
                # Поиск всех пользователей
                query = select(User)
                result = await session.execute(query)
                users = result.scalars().all()

                if not users:
                    return "No users found."

                # Форматирование данных пользователей в строку
                users_info = "\n".join(
                    [
                        f"Username: @{user.username}\n"
                        f"Status: {user.status}\n"
                        f"Last Activity DateTime: {user.last_activity_datetime}\n"
                        for user in users
                    ]
                )

                return users_info

    except Exception as e:
        print(e)
        return ''
