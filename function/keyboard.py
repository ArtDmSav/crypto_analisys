from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from tradingview_ta import Interval

from db.db_connect import write_transaction
from language import en, ru, tr, es

LANGUAGES = {
    'en': en,
    'ru': ru,
    'tr': tr,
    'es': es,
}


async def interval_choose_or_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(lang.CHOOSE_INTERVAL, callback_data="set_interval")],
        [InlineKeyboardButton(lang.LANGUAGE, callback_data="choose_language")
         ]])

    await update.message.reply_html(lang.START_MSG, reply_markup=reply_markup)


async def language_kb(update, context) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    lang_kb = [
        [
            InlineKeyboardButton("English", callback_data='lang_en'),
            InlineKeyboardButton("Español", callback_data='lang_es')
        ],
        [
            InlineKeyboardButton("Türkçe", callback_data='lang_tr'),
            InlineKeyboardButton("Русский", callback_data='lang_ru')
        ],
    ]
    reply_markup = InlineKeyboardMarkup(lang_kb)
    await update.message.reply_html(lang.LANGUAGE, reply_markup=reply_markup)


async def newsletter_chart_msg_kb(recomend: str, price: str, update: Update,
                                  context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]
    trading_pair = context.user_data.get('trading_pair', 'BTCUSDT')

    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(lang.GET_UPDATE, callback_data="newsletter")],
        [InlineKeyboardButton(lang.GET_CHART, callback_data="True")
         ]])

    await update.message.reply_html(recomend, reply_markup=reply_markup)
    # await update.message.reply_text(lang.CHANGE_INTERVAL)
    await write_transaction(update.message.from_user.username,
                            context.user_data.get("interval", Interval.INTERVAL_1_HOUR),
                            trading_pair,
                            price,
                            context.user_data.get('language', 'es'),
                            update.message.chat.id)
    await symbol_kb(update, context)


async def newsletter_chart_clbk_kb(recomend: str, price: str, update: Update,
                                   context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]
    trading_pair = context.user_data.get('trading_pair', 'BTCUSDT')

    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(lang.GET_UPDATE, callback_data="newsletter")],
        [InlineKeyboardButton(lang.GET_CHART, callback_data="True")
         ]])

    await update.callback_query.message.reply_html(recomend, reply_markup=reply_markup)
    # await update.callback_query.message.reply_text(lang.CHANGE_INTERVAL)
    await write_transaction(update.callback_query.from_user.username,
                            context.user_data.get("interval", Interval.INTERVAL_1_HOUR),
                            trading_pair,
                            price,
                            context.user_data.get('language', 'es'),
                            update.callback_query.message.chat.id)
    await symbol_kb(update, context)


async def update_interval_kb(update, context) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    reply_markup = InlineKeyboardMarkup([
        [
            # InlineKeyboardButton(lang.MIN_10, callback_data="00600"),
            InlineKeyboardButton("test10sec", callback_data="00010"),
            InlineKeyboardButton(lang.MIN_30, callback_data="01800"),
            InlineKeyboardButton(lang.HOUR_1, callback_data="03600"),
        ],
        [
            InlineKeyboardButton(lang.HOURS_6, callback_data="21600"),
            InlineKeyboardButton(lang.HOURS_12, callback_data="43200"),
            InlineKeyboardButton(lang.DAY_1, callback_data="86400"),
        ],
    ])
    await update.callback_query.message.reply_html(lang.UPDATE_INTERVAL, reply_markup=reply_markup)


async def interval_kb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    keyboard = [
        [
            InlineKeyboardButton(lang.MIN_1, callback_data=Interval.INTERVAL_1_MINUTE),
            InlineKeyboardButton(lang.MIN_5, callback_data=Interval.INTERVAL_5_MINUTES),
            InlineKeyboardButton(lang.MIN_30, callback_data=Interval.INTERVAL_30_MINUTES),
        ],
        [
            InlineKeyboardButton(lang.HOUR_1, callback_data=Interval.INTERVAL_1_HOUR),
            InlineKeyboardButton(lang.HOURS_4, callback_data=Interval.INTERVAL_4_HOURS),
            InlineKeyboardButton(lang.DAY_1, callback_data=Interval.INTERVAL_1_DAY),
        ],
    ]

    # keyboard = [
    #     [
    #         InlineKeyboardButton(lang.MIN_1, callback_data=Interval.INTERVAL_1_MINUTE),
    #         InlineKeyboardButton(lang.MIN_5, callback_data=Interval.INTERVAL_5_MINUTES),
    #         InlineKeyboardButton(lang.MIN_15, callback_data=Interval.INTERVAL_15_MINUTES)
    #     ],
    #     [
    #         InlineKeyboardButton(lang.MIN_30, callback_data=Interval.INTERVAL_30_MINUTES),
    #         InlineKeyboardButton(lang.HOUR_1, callback_data=Interval.INTERVAL_1_HOUR),
    #         InlineKeyboardButton(lang.HOURS_2, callback_data=Interval.INTERVAL_2_HOURS)
    #     ],
    #     [
    #         InlineKeyboardButton(lang.HOURS_4, callback_data=Interval.INTERVAL_4_HOURS),
    #         InlineKeyboardButton(lang.DAY_1, callback_data=Interval.INTERVAL_1_DAY),
    #         InlineKeyboardButton(lang.WEEK_1, callback_data=Interval.INTERVAL_1_WEEK)
    #     ],
    #     [
    #         InlineKeyboardButton(lang.MONTH_1, callback_data=Interval.INTERVAL_1_MONTH)
    #     ],
    # ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(lang.INTERVALS, reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.message.reply_text(lang.INTERVALS, reply_markup=reply_markup)
        except Exception as e:
            await update.callback_query.edit_message_text(lang.MSG_ERROR)
            print(e)


async def symbol_kb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = context.user_data.get('language', 'es')
    lang = LANGUAGES[user_language]

    keyboard = [
        [
            InlineKeyboardButton("BTCUSDT", callback_data="BTCUSDT"),
            InlineKeyboardButton("ETHUSDT", callback_data="ETHUSDT"),
            InlineKeyboardButton("SOLUSDT", callback_data="SOLUSDT"),
        ],
        [
            InlineKeyboardButton("LTCUSDT", callback_data="LTCUSDT"),
            InlineKeyboardButton("DOTUSDT", callback_data="DOTUSDT"),
            InlineKeyboardButton("NOTUSDT", callback_data="NOTUSDT")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(lang.CHOOSE_PAIR, reply_markup=reply_markup)

    elif update.callback_query:
        try:
            await update.callback_query.message.reply_text(lang.CHOOSE_PAIR,
                                                           reply_markup=reply_markup)
        except Exception as e:
            await update.callback_query.edit_message_text(lang.MSG_ERROR)
            print(e)
