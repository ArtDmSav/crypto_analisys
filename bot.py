import asyncio
import logging
import os
from datetime import datetime

import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from telegram.ext import CallbackQueryHandler, Application, CommandHandler, ContextTypes, MessageHandler, filters
from tradingview_ta import TA_Handler, Interval
from webdriver_manager.chrome import ChromeDriverManager

from config.data import BOT_TOKEN, WAIT_BF_DEL_CHART_PNG
from db.create import create_db
from language import ru, en, tr

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

create_db()

LANGUAGES = {
    'en': en,
    'ru': ru,
    'tr': tr,
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Set default language to English
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]

    keyboard = [
        [InlineKeyboardButton("English", callback_data='lang_en')],
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("Türkçe", callback_data='lang_tr')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(lang.START_MSG, reply_markup=reply_markup)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    choice = query.data

    match choice:
        case 'lang_en':
            context.user_data['language'] = 'en'
        case 'lang_ru':
            context.user_data['language'] = 'ru'
        case 'lang_tr':
            context.user_data['language'] = 'tr'

    lang = LANGUAGES[context.user_data['language']]
    await query.edit_message_text(lang.START_MSG)
    await set_interval(update, context)

    # Update bot commands based on the new language
    await set_bot_commands(context.application, context.user_data['language'])


async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]

    keyboard = [
        [
            InlineKeyboardButton(lang.MIN_1, callback_data=Interval.INTERVAL_1_MINUTE),
            InlineKeyboardButton(lang.MIN_5, callback_data=Interval.INTERVAL_5_MINUTES),
            InlineKeyboardButton(lang.MIN_15, callback_data=Interval.INTERVAL_15_MINUTES)
        ],
        [
            InlineKeyboardButton(lang.MIN_30, callback_data=Interval.INTERVAL_30_MINUTES),
            InlineKeyboardButton(lang.HOUR_1, callback_data=Interval.INTERVAL_1_HOUR),
            InlineKeyboardButton(lang.HOURS_2, callback_data=Interval.INTERVAL_2_HOURS)
        ],
        [
            InlineKeyboardButton(lang.HOURS_4, callback_data=Interval.INTERVAL_4_HOURS),
            InlineKeyboardButton(lang.DAY_1, callback_data=Interval.INTERVAL_1_DAY),
            InlineKeyboardButton(lang.WEEK_1, callback_data=Interval.INTERVAL_1_WEEK)
        ],
        [
            InlineKeyboardButton(lang.MONTH_1, callback_data=Interval.INTERVAL_1_MONTH)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(lang.INTERVALS, reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.message.reply_text(lang.INTERVALS, reply_markup=reply_markup)
        except:
            await update.callback_query.edit_message_text(lang.MSG_ERROR)


async def interval_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]

    usr_interval = update.callback_query.data

    context.user_data['interval'] = usr_interval
    await update.callback_query.answer()  # Уведомляем Telegram, что запрос обработан
    match usr_interval:
        case "1m":
            show_usr_interval = lang.MIN_1
            screenshot_interval = "1"
        case "5m":
            show_usr_interval = lang.MIN_5
            screenshot_interval = "5"
        case "15m":
            show_usr_interval = lang.MIN_15
            screenshot_interval = "15"
        case "30m":
            show_usr_interval = lang.MIN_30
            screenshot_interval = "30"
        case "1h":
            show_usr_interval = lang.HOUR_1
            screenshot_interval = "60"
        case "2h":
            show_usr_interval = lang.HOURS_2
            screenshot_interval = "120"
        case "4h":
            show_usr_interval = lang.HOURS_4
            screenshot_interval = "240"
        case "1d":
            show_usr_interval = lang.DAY_1
            screenshot_interval = "D"
        case "1W":
            show_usr_interval = lang.WEEK_1
            screenshot_interval = "W"
        case "1M":
            show_usr_interval = lang.MONTH_1
            screenshot_interval = "M"
        case _:
            show_usr_interval = lang.MSG_ERROR
    context.user_data['show_usr_interval'] = show_usr_interval
    context.user_data['screenshot_interval'] = screenshot_interval
    await update.callback_query.edit_message_text(f"{lang.U_INTERVAL}{show_usr_interval}\n\n{lang.EXAMPLE_PAIR}")


async def info_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]
    await update.message.reply_text(lang.INFO_BOT)


async def info_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]
    await update.message.reply_text(lang.INFO_INTERVAL)


async def get_tradingview_screenshot(interval: str, trading_pair: str, time_stamp: str) -> None:
    # Настройка Selenium
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = f"https://www.tradingview.com/chart/?symbol={trading_pair}&interval={interval}"
    driver.get(url)

    # Найти элемент, содержащий график
    chart_element = driver.find_element(By.CSS_SELECTOR, '.chart-container')
    screenshot = chart_element.screenshot_as_png
    filename = os.path.join('picture', f'{time_stamp}_{trading_pair}.png')

    with open(filename, 'wb') as file:
        file.write(screenshot)
    driver.quit()


# async def chart_png(usr_interval, trading_pair, time_stamp):
#     limit = 50
#
#     name_png = os.path.join('picture', f'{time_stamp}_{trading_pair}.png')
#     exchange = ccxt.binance()
#     ohlcv = await exchange.fetch_ohlcv(trading_pair, timeframe=usr_interval, limit=limit)
#     await exchange.close()
#     data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#     data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
#     data.set_index('timestamp', inplace=True)
#     # Построение графика
#     mpf.plot(data, type='candle', style='charles', title=trading_pair, ylabel='',
#              volume=False, savefig=name_png)


async def analisys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global recomendation
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]
    error = False

    usr_interval = context.user_data.get("interval", Interval.INTERVAL_1_HOUR)
    show_usr_interval = context.user_data.get("show_usr_interval", lang.HOUR_1)
    trading_pair = update.message.text.strip()
    context.user_data['trading_pair'] = trading_pair
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={trading_pair.upper()}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                data = await response.json()
                await update.message.reply_text(f"{lang.PAIR_PRICE}{trading_pair}: {data['price']}")
    except Exception as e:
        error = True
        await update.message.reply_text(lang.INVALID_SYMBOL)

    if not error:
        try:
            response = TA_Handler(
                symbol=trading_pair,
                screener="crypto",
                exchange="BINANCE",
                interval=usr_interval
            )

            match response.get_analysis().summary["RECOMMENDATION"]:
                case 'BUY':
                    recomendation = f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.BUY}"
                    # await update.message.reply_text(lang.BUY)
                case 'STRONG_BUY':
                    recomendation = f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.STRONG_BUY}"
                    # await update.message.reply_text(lang.STRONG_BUY)
                case 'SELL':
                    recomendation = f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.SELL}"
                    # await update.message.reply_text(lang.SELL)
                case 'STRONG_SELL':
                    recomendation = f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.STRONG_SELL}"
                    # await update.message.reply_text(lang.STRONG_SELL)
                case 'NEUTRAL':
                    recomendation = f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.NEUTRAL}"
                    # await update.message.reply_text(lang.NEUTRAL)
                case _:
                    await update.message.reply_text(lang.MSG_ERROR)
                    error = True

        except Exception as e:
            await update.message.reply_text(lang.REQUEST_ERROR)
            error = True

    if not error:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(lang.GET_CHART, callback_data="True")]])
        await update.message.reply_html(recomendation, reply_markup=reply_markup)
        await update.message.reply_text(lang.CHANGE_INTERVAL)

        # Собираем график из данных
        # try:
        #     await chart_png(usr_interval, trading_pair, str(time_stamp))
        # except:
        #     await update.message.reply_text(lang.MSG_ERROR)
        #     await update.message.reply_text(lang.CHANGE_INTERVAL)
        # else:
        #     name_png = os.path.join('picture', f'{trading_pair}_{time_stamp}.png')
        #     with open(name_png, 'rb') as file:
        #         await update.message.reply_photo(file)
        #     os.remove(name_png)


async def get_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]
    query = update.callback_query
    await query.answer()
    choice = query.data
    if choice == "True":
        await query.message.reply_text(lang.BUILD_CHART)
        time_stamp = datetime.now()
        trading_pair = context.user_data.get("trading_pair", "BTCUSDT")
        try:
            screenshot_interval = context.user_data.get("screenshot_interval", '60')
            await get_tradingview_screenshot(screenshot_interval, trading_pair, str(time_stamp))
            name_png = os.path.join('picture', f'{time_stamp}_{trading_pair}.png')
            with open(name_png, 'rb') as file:
                await query.message.reply_photo(file)
            await asyncio.sleep(WAIT_BF_DEL_CHART_PNG)
            os.remove(name_png)

        except Exception as e:
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
    application.add_handler(CallbackQueryHandler(interval_choice))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analisys))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
