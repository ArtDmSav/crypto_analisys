import asyncio
import logging
import os
import re
from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, Application, CommandHandler, ContextTypes, MessageHandler, filters
from tradingview_ta import Interval

from config.data import BOT_TOKEN, WAIT_BF_DEL_CHART_PNG, ADMIN_USERNAME
from db.db_connect import add_user, deactivate_user, check_user_exists, write_transaction, get_user_info, \
    get_last_10_transactions
from function.keyboard import lang_kb, symbol_kb, interval_kb
from function.symbol_chart import get_tradingview_screenshot
from function.trading_request import tr_view_msg, tr_view_bt, price_before_24h
from language import ru, en, tr, es

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

LANGUAGES = {
    'en': en,
    'ru': ru,
    'tr': tr,
    'es': es,
}


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in ADMIN_USERNAME:
        # Используем регулярное выражение для извлечения аргумента после команды /add
        match = re.match(r"^/add\s@([a-zA-Z0-9]{1,30})$", update.message.text)
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


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in ADMIN_USERNAME:
        # Используем регулярное выражение для извлечения аргумента после команды /add
        match = re.match(r"^/stop\s@([a-zA-Z0-9]{1,30})$", update.message.text)
        if match:
            add_value = match.group(1)
            status = await deactivate_user(add_value)

            if status:
                await update.message.reply_text(f"Вы деактивировали user: {add_value}")
            else:
                await update.message.reply_text(f"User: {add_value}, не найден!")

        else:
            await update.message.reply_text("Пожалуйста, укажите значение после команды /stop длиной до 30 символов.")
    else:
        await update.message.reply_text("Вы не являетесь админом бота")


async def u_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in ADMIN_USERNAME:
        # Используем регулярное выражение для извлечения аргумента после команды /add
        match = re.match(r"^/u_info\s@([a-zA-Z0-9]{1,30})$", update.message.text)
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
        await update.message.reply_text("Вы не являетесь админом бота")


async def tr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in ADMIN_USERNAME:
        # Используем регулярное выражение для извлечения аргумента после команды /add
        match = re.match(r"^/tr\s@([a-zA-Z0-9]{1,30})$", update.message.text)
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


async def info_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]
    await update.message.reply_text(lang.INFO_BOT)


async def info_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]
    await update.message.reply_text(lang.INFO_INTERVAL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    if await check_user_exists(update.message.from_user.username):
        reply_markup = InlineKeyboardMarkup(lang_kb)
        await update.message.reply_html(lang.START_MSG, reply_markup=reply_markup)
    else:
        await update.message.reply_text(lang.MSG_ERROR)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    choice = query.data

    match choice:
        case 'lang_en':
            context.user_data['language'] = 'en'
        case 'lang_es':
            context.user_data['language'] = 'es'
        case 'lang_tr':
            context.user_data['language'] = 'tr'
        case 'lang_ru':
            context.user_data['language'] = 'ru'

    lang = LANGUAGES[context.user_data['language']]
    await query.edit_message_text(lang.START_MSG)
    await set_interval(update, context)

    # Update bot commands based on the new language
    # await set_bot_commands(context.application, context.user_data['language'])


async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    if await check_user_exists(update.callback_query.from_user.username):
        await interval_kb(update, context)
    else:
        await update.message.reply_text(lang.MSG_ERROR)


async def interval_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    query = update.callback_query
    await query.answer()
    usr_interval = query.data

    context.user_data['interval'] = usr_interval
    await update.callback_query.answer()  # Уведомляем Telegram, что запрос обработан

    # Delete key board
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    intervals = {
        "1m": ("1", lang.MIN_1),
        "5m": ("5", lang.MIN_5),
        "15m": ("15", lang.MIN_15),
        "30m": ("30", lang.MIN_30),
        "1h": ("60", lang.HOUR_1),
        "2h": ("120", lang.HOURS_2),
        "4h": ("240", lang.HOURS_4),
        "1d": ("D", lang.DAY_1),
        "1W": ("W", lang.WEEK_1),
        "1M": ("M", lang.MONTH_1)
    }

    if usr_interval in intervals:
        screenshot_interval, show_usr_interval = intervals[usr_interval]
        context.user_data['interval'] = usr_interval
        context.user_data['show_usr_interval'] = show_usr_interval
        context.user_data['screenshot_interval'] = screenshot_interval

        # await update.callback_query.edit_message_text(f"{lang.U_INTERVAL}{show_usr_interval}\n\n{lang.EXAMPLE_PAIR}")
        await symbol_kb(update, context)

    else:

        await update.callback_query.edit_message_text(lang.MSG_ERROR)
        await symbol_kb(update, context)


async def analisys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    error = False
    if update.callback_query and await check_user_exists(update.callback_query.from_user.username):
        query = update.callback_query
        await query.answer()
        trading_pair = query.data
        context.user_data['trading_pair'] = trading_pair
        # Delete key board
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        # price = await tr_price(trading_pair)

        max_price, min_price, price_change_percent, price = await price_before_24h(trading_pair)

        if price:
            await update.callback_query.message.reply_text(f"\n\n-------------------------------\n"
                                                           f"📊*{trading_pair}{lang.PAIR_PRICE}:* {price}\n"
                                                           f"-------------------------------\n\n"
                                                           f"↕️*{lang.PAIR_CHANGE}:* {price_change_percent}%\n"
                                                           f"📈*{lang.PAIR_MAX}:* {max_price}\n"
                                                           f"📉*{lang.PAIR_MIN}:* {min_price}",
                                                           parse_mode=ParseMode.MARKDOWN)
        else:
            error = True
            await update.callback_query.message.reply_text(lang.INVALID_SYMBOL)

        if not error:
            recomendation = await tr_view_bt(trading_pair, update, context)
            # if {recomendation} empty it's == error
            error = False if recomendation else True

        if not error:
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(lang.GET_CHART, callback_data="True")]])

            await update.callback_query.message.reply_html(recomendation, reply_markup=reply_markup)
            await update.callback_query.message.reply_text(lang.CHANGE_INTERVAL)
            await symbol_kb(update, context)
            await write_transaction(update.callback_query.from_user.username,
                                    context.user_data.get("interval", Interval.INTERVAL_1_HOUR),
                                    trading_pair,
                                    price,
                                    update.callback_query.from_user.language_code)

    elif await check_user_exists(update.message.from_user.username):
        trading_pair = update.message.text.strip().upper()
        context.user_data['trading_pair'] = trading_pair

        # price = await tr_price(trading_pair)
        max_price, min_price, price_change_percent, price = await price_before_24h(trading_pair)

        if price:
            await update.message.reply_text(f"\n\n-------------------------------\n"
                                            f"📊*{trading_pair}{lang.PAIR_PRICE}:* {price}\n"
                                            f"-------------------------------\n\n"
                                            f"↕️*{lang.PAIR_CHANGE}:* {price_change_percent}%\n"
                                            f"📈*{lang.PAIR_MAX}:* {max_price}\n"
                                            f"📉*{lang.PAIR_MIN}:* {min_price}",
                                            parse_mode=ParseMode.MARKDOWN)
        else:
            error = True
            await update.message.reply_text(lang.INVALID_SYMBOL)

        if not error:
            recomendation = await tr_view_msg(trading_pair, update, context)
            # if {recomendation} empty it's == error
            error = False if recomendation else True

        if not error:
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(lang.GET_CHART, callback_data="True")]])
            await update.message.reply_html(recomendation, reply_markup=reply_markup)
            await update.message.reply_text(lang.CHANGE_INTERVAL)
            await symbol_kb(update, context)
            await write_transaction(update.message.from_user.username,
                                    context.user_data.get("interval", Interval.INTERVAL_1_HOUR),
                                    trading_pair,
                                    price,
                                    update.message.from_user.language_code)
    else:
        await update.message.reply_text(lang.MSG_ERROR)


async def get_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]

    query = update.callback_query
    await query.answer()

    # Delete key board
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    picture_dir = os.path.join(base_dir, 'picture')

    if not os.path.exists(picture_dir):
        os.makedirs(picture_dir)
    await query.answer()
    choice = query.data
    if choice == "True":
        await query.message.reply_text(lang.BUILD_CHART)
        time_stamp = datetime.now()
        trading_pair = context.user_data.get("trading_pair", "BTCUSDT")
        try:
            screenshot_interval = context.user_data.get("screenshot_interval", '60')
            await get_tradingview_screenshot(screenshot_interval, trading_pair, str(time_stamp))
            name_png = os.path.join(picture_dir, f'{time_stamp}_{trading_pair}.png')
            with open(name_png, 'rb') as file:
                await query.message.reply_photo(file)

            await asyncio.sleep(WAIT_BF_DEL_CHART_PNG)
            os.remove(name_png)

        except Exception as e:
            print(e)
            pass


async def set_bot_commands(application: Application, language: str) -> None:
    lang = LANGUAGES[language]

    commands = [
        BotCommand("start", en.BOT_START),
        BotCommand("set_interval", en.SET_INTERVAL),
        BotCommand("info_bot", en.ABOUT_BOT),
        BotCommand("info_interval", en.INTERVAL_WHAT_IS_IT),
    ]

    await application.bot.set_my_commands(commands)
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def on_startup(application: Application) -> None:
    # Set default language to English if not specified
    default_language = 'en'
    await set_bot_commands(application, default_language)


def main() -> None:
    """Start the bot."""
    # application = Application.builder().token(BOT_TOKEN).post_init(on_startup).build() # Change menu lang
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_interval", set_interval))
    application.add_handler(CommandHandler("info_bot", info_bot))
    application.add_handler(CommandHandler("info_interval", info_interval))

    application.add_handler(CallbackQueryHandler(get_chart, pattern='^True$'))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(analisys, pattern='^[A-Z]{3,5}[A-Z]{3,5}$'))
    application.add_handler(CallbackQueryHandler(interval_choice))

    # обработчики команд админа
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("u_info", u_info))
    application.add_handler(CommandHandler("tr", tr))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analisys))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interval_choice))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
