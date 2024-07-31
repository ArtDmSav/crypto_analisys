from datetime import datetime

from sqlalchemy import update, func, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base
from telegram import Update
from telegram.ext import ContextTypes

from config.data import DEFAULT_LANGUAGE
from db.db_create import Operations, User

DATABASE_URL = "postgresql+asyncpg://admin:password@localhost/crypto"

# Создаем движок базы данных
engine = create_async_engine(DATABASE_URL, echo=False)

# Создаем базовый класс для объявлений моделей
Base = declarative_base()

# Создаем асинхронную сессию
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def add_user(username: str,
                   update: Update,
                   language='xz',
                   ) -> int:
    try:
        async with async_session() as session:
            async with session.begin():
                # Проверяем, существует ли пользователь с таким же именем
                query = select(User).where(User.username == username)
                result = await session.execute(query)
                user = result.scalars().first()

                if user:
                    # Обновляем статус пользователя

                    user.registration_datetime = func.now()
                    user.status = 720
                    await session.commit()
                    return 2

                # Добавляем нового пользователя
                new_user = User(
                    username=username,
                    registration_datetime=func.now(),
                    last_activity_datetime=func.now(),
                    language=language,
                    status=720
                )
                session.add(new_user)
                await session.commit()
                return 1
    except Exception as e:
        await update.message.reply_text(f"error: {e}")
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
                    "username": user.username,
                    "chat_id": user.chat_id,
                    "trading_pair": user.trading_pair,
                    "interval": user.interval,
                    "update_time": user.update_time,
                    "update_interval": user.update_interval,
                    "language": user.language
                }
                for user in users
            ]
            return users_info


async def update_status(username: str, status: bool, update_interval: int = 86400) -> None:
    async with async_session() as session:
        async with session.begin():
            # Поиск пользователя по username
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalars().first()

            if user is None:
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
                return

            # Обновление поле
            user.update_time = update_time
            session.add(user)
            await session.commit()


async def check_user_exists(username: str) -> bool:
    async with async_session() as session:
        async with session.begin():
            query = select(User).where(User.username == username, User.status > 0)
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
                # new_operation = Operations(
                #     user_id=user.id,
                #     datetime=datatime,
                #     interval=interval,
                #     trading_pair=trading_pair,
                #     price=price
                # )
                # session.add(new_operation)
                await session.commit()
                print(f"Transaction for user {username} added successfully.")
    except Exception as e:
        print(e)


async def update_user_language(username: str, language: str) -> None:
    async with async_session() as session:
        async with session.begin():
            # Поиск пользователя по username
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalars().first()

            if user is None:
                print(f"User with username {username} not found.")
                return

            # Обновление поля language
            user.language = language
            session.add(user)
            await session.commit()
            print(f"User {username}'s language updated to {language}.")


async def delete_user(username: str) -> bool:
    async with async_session() as session:
        async with session.begin():
            # Поиск пользователя по username
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalars().first()

            if user is None:
                print(f"User with username {username} not found.")
                return False

            # Удаление пользователя
            await session.delete(user)
            await session.commit()
            print(f"User {username} deleted successfully.")
            return True


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
                        f"№ {user.id}\n"
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


async def add_user_24_access(username: str, language: str = 'xz') -> None:
    async with async_session() as session:
        async with session.begin():
            # Поиск пользователя по username
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            user = result.scalars().first()

            if user is None:
                # Создание нового пользователя
                new_user = User(
                    username=username,
                    registration_datetime=func.now(),
                    last_activity_datetime=func.now(),
                    language=language,
                    status=24
                )
                session.add(new_user)
                await session.commit()
                print(f"New user {username} created.")
            else:
                print(f"User with username {username} already exists.")


async def check_users_for_finsh_time() -> None:
    async with async_session() as session:
        async with session.begin():
            # Получение текущего времени
            now = datetime.now()

            # Обработка пользователей со статусом 24
            result_24 = await session.execute(select(User).where(User.status == 24))
            users_24 = result_24.scalars().all()

            for user in users_24:
                time_difference = now - user.registration_datetime
                hours_difference = time_difference.total_seconds() / 3600

                if hours_difference > user.status:
                    user.status = 0
                    session.add(user)

            # Обработка пользователей со статусом 720
            result_720 = await session.execute(select(User).where(User.status == 720))
            users_720 = result_720.scalars().all()

            for user in users_720:
                time_difference = now - user.registration_datetime
                hours_difference = time_difference.total_seconds() / 3600

                if hours_difference > user.status:
                    user.status = -1
                    session.add(user)

            # Подтверждение всех изменений в транзакции
            await session.commit()


async def delete_all_operations() -> None:
    async with async_session() as session:
        async with session.begin():
            # Удаление всех записей из таблицы operations
            await session.execute(delete(Operations))
            await session.commit()
            print("All operations deleted successfully.")


async def find_and_set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'language' not in context.user_data:
        try:
            lang_code = await get_user_language(update.message.from_user.username)
        except AttributeError:
            lang_code = await get_user_language(update.callback_query.from_user.username)

        context.user_data['language'] = lang_code if lang_code else DEFAULT_LANGUAGE


async def get_user_language(username: str) -> str:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User.language).where(User.username == username)
            )
            language = result.scalar_one_or_none()
            return language if language is not None else ''
