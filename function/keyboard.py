from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from tradingview_ta import Interval

from language import en, ru, tr, es

LANGUAGES = {
    'en': en,
    'ru': ru,
    'tr': tr,
    'es': es,
}

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
