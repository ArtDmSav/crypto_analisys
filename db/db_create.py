import asyncio
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+asyncpg://admin:password@localhost/crypto"

# Создаем движок базы данных
engine = create_async_engine(DATABASE_URL, echo=False)

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


# Определяем модель для таблицы operations
class Operations(Base):
    __tablename__ = 'operations'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    datetime = sa.Column(sa.DateTime, nullable=False)
    interval = sa.Column(sa.String(5), nullable=False)
    trading_pair = sa.Column(sa.String(10), nullable=False)
    price = sa.Column(sa.Numeric(18, 8), nullable=False)


# Создаем функцию для создания таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
