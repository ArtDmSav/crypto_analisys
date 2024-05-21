import logging
import aiohttp
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from telegram.ext import CallbackQueryHandler, Application, CommandHandler, ContextTypes, MessageHandler, filters

from config.data import BOT_TOKEN
from db.create import create_db
from db.commit import write_user, user_request
from language import ru, en

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
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Set default language to English
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]

    keyboard = [
        [InlineKeyboardButton("English", callback_data='lang_en')],
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(lang.START_MSG, reply_markup=reply_markup)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == 'lang_en':
        context.user_data['language'] = 'en'
    elif choice == 'lang_ru':
        context.user_data['language'] = 'ru'

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

    print(usr_interval)
    context.user_data['interval'] = usr_interval
    await update.callback_query.answer()  # Уведомляем Telegram, что запрос обработан
    match usr_interval:
        case "1m":
            show_usr_interval = lang.MIN_1
        case "5m":
            show_usr_interval = lang.MIN_5
        case "15m":
            show_usr_interval = lang.MIN_15
        case "30m":
            show_usr_interval = lang.MIN_30
        case "1h":
            show_usr_interval = lang.HOUR_1
        case "2h":
            show_usr_interval = lang.HOURS_2
        case "4h":
            show_usr_interval = lang.HOURS_4
        case "1d":
            show_usr_interval = lang.DAY_1
        case "1W":
            show_usr_interval = lang.WEEK_1
        case "1M":
            show_usr_interval = lang.MONTH_1
        case _:
            show_usr_interval = lang.MSG_ERROR
            print(lang.MSG_ERROR)
    context.user_data['show_usr_interval'] = show_usr_interval
    await update.callback_query.edit_message_text(f"{lang.U_INTERVAL}{show_usr_interval}\n\n{lang.EXAMPLE_PAIR}")


async def info_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]
    await update.message.reply_text(lang.INFO_BOT)


async def info_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]
    await update.message.reply_text(lang.INFO_INTERVAL)


async def analisys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]

    usr_interval = context.user_data.get("interval", Interval.INTERVAL_1_HOUR)
    show_usr_interval = context.user_data.get("show_usr_interval", lang.HOUR_1)
    print(usr_interval)
    trading_pair = update.message.text.strip()
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={trading_pair.upper()}"

    try:
        async with aiohttp.ClientSession() as session:  # Создание сессии
            async with session.get(url, ssl=False) as response:  # Запрос в пределах сессии
                data = await response.json()
                await update.message.reply_text(f"{lang.PAIR_PRICE}{trading_pair}: {data['price']}")
    except:
        await update.message.reply_text(lang.ERROR_PRICE)

    try:
        response = TA_Handler(
            symbol=trading_pair,
            screener="crypto",
            exchange="BINANCE",
            interval=usr_interval
        )

        await update.message.reply_text(f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}")
        match response.get_analysis().summary["RECOMMENDATION"]:
            case 'BUY':
                await update.message.reply_text(lang.BUY)
            case 'STRONG_BUY':
                await update.message.reply_text(lang.STRONG_BUY)
            case 'SELL':
                await update.message.reply_text(lang.SELL)
            case 'STRONG_SELL':
                await update.message.reply_text(lang.STRONG_SELL)
            case 'NEUTRAL':
                await update.message.reply_text(lang.NEUTRAL)
            case _:
                await update.message.reply_text(lang.MSG_ERROR)
                print(lang.MSG_ERROR)

        await update.message.reply_text(lang.CHANGE_INTERVAL)
    except:
        await update.message.reply_text(lang.REQUEST_ERROR)

    await write_user(
        update.effective_chat.id,
        update.effective_user.username,
        update.effective_user.first_name,
        update.effective_user.last_name,
        update.effective_user.language_code,
        usr_interval
    )
    await user_request(
        update.effective_chat.id,
        usr_interval,
        trading_pair,
        str(datetime.now())
    )


async def set_bot_commands(application: Application, language: str) -> None:
    lang = LANGUAGES[language]

    commands = [
        BotCommand("start", lang.BOT_START),
        BotCommand("set_interval", lang.SET_INTERVAL),
        BotCommand("info_bot", lang.ABOUT_BOT),
        BotCommand("info_interval", lang.INTERVAL_WHAT_IS_IT),
    ]

    await application.bot.set_my_commands(commands)
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def on_startup(application: Application) -> None:
    # Set default language to English if not specified
    default_language = 'en'
    await set_bot_commands(application, default_language)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).post_init(on_startup).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_interval", set_interval))
    application.add_handler(CommandHandler("info_bot", info_bot))
    application.add_handler(CommandHandler("info_interval", info_interval))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(interval_choice))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analisys))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
