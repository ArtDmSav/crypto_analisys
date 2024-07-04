import re

from telegram import Update
from telegram.ext import ContextTypes

from config.data import ADMIN_USERNAME
from db.db_connect import add_user, deactivate_user, get_user_info, get_last_10_transactions


async def add_command_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in ADMIN_USERNAME:
        # Используем регулярное выражение для извлечения аргумента после команды /add
        match = re.match(r'/add\s+@?(\w{5,32})', update.message.text)
        await update.message.reply_text(f" {match}")
        if match:
            add_value = match.group(1)
            status = await add_user(add_value)

            match status:
                case 1:
                    await update.message.reply_text(f"Вы добавили user: {add_value}")
                case 2:
                    await update.message.reply_text(f"User: {add_value}, был добавлен ранне.\n"
                                                    f"Доступ предоставлен повторно")
                case 0:
                    await update.message.reply_text(f"Произошла ошибка записи в БД попробуйте снова")

        else:
            await update.message.reply_text("Пожалуйста, укажите значение после команды /add длиной до 30 символов.")
    else:
        await update.message.reply_text("Вы не являетесь админом бота")


async def stop_command_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in ADMIN_USERNAME:
        match = re.match(r'/stop\s+@?(\w{5,32})', update.message.text)
        if match:
            add_value = match.group(1)
            status = await deactivate_user(add_value)

            if status:
                await update.message.reply_text(f"Вы деактивировали user: {add_value}")
            else:
                await update.message.reply_text(f"User: {add_value}, не найден!")

        else:
            await update.message.reply_text(
                "Ошибка ввода\nПожалуйста, укажите значение после команды /stop длиной до 30 символов.")
    else:
        await update.message.reply_text("Access error")


async def u_info_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in ADMIN_USERNAME:
        # Используем регулярное выражение для извлечения аргумента после команды /add
        match = re.match(r'/u_info\s+@?(\w{5,32})', update.message.text)
        if match:
            add_value = match.group(1)
            user_info = await get_user_info(add_value)

            if user_info:
                await update.message.reply_text(user_info)
            else:
                await update.message.reply_text("Ошибка запроса в БД")
        else:
            await update.message.reply_text("Пожалуйста, укажите значение после команды /u_info.")
    else:
        await update.message.reply_text("Access error")


async def last_10_transaction_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in ADMIN_USERNAME:
        # Используем регулярное выражение для извлечения аргумента после команды /add
        match = re.match(r'/tr\s+@?(\w{5,32})', update.message.text)
        if match:
            add_value = match.group(1)
            user_info = await get_last_10_transactions(add_value)

            if user_info:
                await update.message.reply_text(user_info)
            else:
                await update.message.reply_text("Ошибка запроса в БД")
        else:
            await update.message.reply_text("Пожалуйста, укажите значение после команды /u_tr.")
    else:
        await update.message.reply_text("Вы не являетесь админом бота")
