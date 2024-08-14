import asyncio
import logging
import os
from datetime import datetime, timedelta
from time import sleep

from telegram import Update, BotCommand, MenuButtonCommands
from telegram.constants import ParseMode
from telegram.error import TelegramError, TimedOut, RetryAfter, NetworkError
from telegram.ext import CallbackQueryHandler, Application, CommandHandler, ContextTypes, MessageHandler, filters

from config.data import BOT_TOKEN, WAIT_BF_DEL_CHART_PNG, SLEEP_TIME, DAY_COUNT, DEFAULT_LANGUAGE, LANGUAGES
from db.db_connect import check_user_exists, update_status, update_pair, update_update_time, check_users_for_finsh_time, \
    add_user_24_access, find_and_set_lang, update_user_language
from function.admin_part import add_command_admin, stop_command_admin, u_info_admin, admin, \
    lst, del_user, del_all_operations
from function.keyboard import symbol_kb, interval_kb, newsletter_chart_clbk_kb, \
    newsletter_chart_msg_kb, update_interval_kb, language_kb, interval_choose_or_language
from function.symbol_chart import get_tradingview_screenshot
from function.trading_request import tr_view_msg, tr_view_bt, price_before_24h, update_tr_view_bt

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


async def transactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # await last_10_transaction_admin(update, context)
    pass


async def info_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]

    await update.message.reply_text(lang.INFO_BOT)


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]
    await update.message.reply_text(lang.SUPPORT_USERNAME)


async def info_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]
    await update.message.reply_text(lang.INFO_INTERVAL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]

    if update.message.from_user.username:
        await add_user_24_access(update.message.from_user.username, update.message.from_user.id)

        if await check_user_exists(update.message.from_user.username):
            await update_status(update.message.from_user.username, False)
            await interval_choose_or_language(update, context)
            # await language_kb(update, context)
        else:
            await update.message.reply_text(lang.ACCESS_ERROR)
    else:
        await update.message.reply_text(lang.USER_ADD_ERROR)


async def set_interval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await set_interval(update, context)


async def choose_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    try:
        await context.bot.delete_message(chat_id=update.callback_query.from_user.id,
                                         message_id=context.user_data['interval_choose_or_language_msg_id'])

    except Exception as e:
        print(1, e)
    # Создаем объект Update для команды /set_interval
    command_update = Update(update.update_id, message=update.callback_query.message)
    # Вызываем обработчик команды /set_interval
    await language_kb(command_update, context)


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
        case _:
            context.user_data['language'] = DEFAULT_LANGUAGE

    lang = LANGUAGES[context.user_data['language']]
    await update_user_language(update.callback_query.from_user.username,
                               update.callback_query.from_user.id,
                               context.user_data['language'])
    await query.edit_message_text(lang.START_MSG)
    await set_interval(update, context)

    # Update bot commands based on the new language
    # await set_bot_commands(context.application, context.user_data['language'])


async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]
    if update.callback_query and await check_user_exists(update.callback_query.from_user.username):
        await update_status(update.callback_query.from_user.username, False)
        await interval_kb(update, context)
    elif await check_user_exists(update.message.from_user.username):
        await update_status(update.message.from_user.username, False)
        await interval_kb(update, context)
    else:
        if update.callback_query:
            await update.callback_query.message.reply_text(lang.MSG_ERROR)
        else:
            await update.message.reply_text(lang.ACCESS_ERROR)


async def interval_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]

    query = update.callback_query
    await query.answer()
    usr_interval = query.data

    context.user_data['interval'] = usr_interval
    await update.callback_query.answer()  # Уведомляем Telegram, что запрос обработан

    # Delete keyboard
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
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]

    error = False
    if update.callback_query and await check_user_exists(update.callback_query.from_user.username):
        query = update.callback_query
        await query.answer()
        trading_pair = query.data
        context.user_data['trading_pair'] = trading_pair
        # Delete keyboard
        await update.callback_query.edit_message_reply_markup(reply_markup=None)

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
            recomend = await tr_view_bt(trading_pair, update, context)
            error = False if recomend else True

        if not error:
            await update_status(update.callback_query.from_user.username, False)
            await newsletter_chart_clbk_kb(recomend, price, update, context)

    elif update.message and (await check_user_exists(update.message.from_user.username) and
                             await check_user_exists(update.message.from_user.username)):
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
            recomend = await tr_view_msg(trading_pair, update, context)
            # if {recomend} empty it's == error
            error = False if recomend else True

        if not error:
            await update_status(update.message.from_user.username, False)
            await newsletter_chart_msg_kb(recomend, price, update, context)

    else:
        await update.message.reply_text(lang.ACCESS_ERROR)


async def get_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]

    query = update.callback_query
    await query.answer()

    # Delete keyboard
    # await update.callback_query.edit_message_reply_markup(reply_markup=None)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    picture_dir = os.path.join(base_dir, 'picture')

    if not os.path.exists(picture_dir):
        os.makedirs(picture_dir)
    await query.answer()
    # choice = query.data
    # if choice == "True":
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


async def update_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Delete keyboard
    # await update.callback_query.edit_message_reply_markup(reply_markup=None)
    try:
        await context.bot.delete_message(chat_id=update.callback_query.from_user.id,
                                         message_id=context.user_data['newsletter_chart_msg_id'])

    except Exception as e:
        print(2, e)
    try:
        await context.bot.delete_message(chat_id=update.callback_query.from_user.id,
                                         message_id=context.user_data['symbol_kb_msg_id'])

    except Exception as e:
        print(3, e)

    # await update_status(update.callback_query.from_user.username, True)
    await update_interval_kb(update, context)


async def update_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]

    query = update.callback_query
    await query.answer()
    try:
        await context.bot.delete_message(chat_id=update.callback_query.from_user.id,
                                         message_id=context.user_data['update_interval_kb_msg_id'])

    except Exception as e:
        print(4, e)

    # Delete keyboard
    # await update.callback_query.edit_message_reply_markup(reply_markup=None)
    # Удаляем текст и клавиатуру
    # await update.callback_query.edit_message_text(text=f"{lang.UPDATE_INTERVAL}", reply_markup=None)

    await update_status(update.callback_query.from_user.username, True, int(query.data))

    await update.callback_query.message.reply_text(lang.SET_UPDATE)


async def update_loop(application: Application) -> None:
    count = 0
    while True:
        count += 1
        users = await update_pair()
        now = datetime.now()
        for user in users:
            try:
                if now - user['update_time'] > timedelta(seconds=user['update_interval']):
                    max_price, min_price, price_change_percent, price = await price_before_24h(user['trading_pair'])
                    lang = LANGUAGES[user['language']]
                    recomend = await update_tr_view_bt(user['trading_pair'], lang, user['interval'])
                    await update_update_time(user['chat_id'], now)
                    try:
                        trading_pair = user['trading_pair'].replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                               '&gt;').replace(
                            '"', '&quot;')
                        pair_price = lang.PAIR_PRICE.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                        '&gt;').replace(
                            '"', '&quot;')
                        pair_change = lang.PAIR_CHANGE.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                          '&gt;').replace(
                            '"', '&quot;')
                        pair_max = lang.PAIR_MAX.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                    '&gt;').replace('"',
                                                                                                                    '&quot;')
                        pair_min = lang.PAIR_MIN.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                    '&gt;').replace('"',
                                                                                                                    '&quot;')
                        stop_update = lang.STOP_UPDATE.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                          '&gt;').replace(
                            '"', '&quot;')
                        recomend_escaped = recomend.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                                                       '&gt;').replace(
                            '"', '&quot;')

                        # Формирование сообщения
                        message = (
                            f"📊<b>{trading_pair}{pair_price}:</b> {price}\n"
                            f"<b>-------------------------------</b>\n\n"
                            f"↕️<b>{pair_change}:</b> {price_change_percent}%\n"
                            f"📈<b>{pair_max}:</b> {max_price}\n"
                            f"📉<b>{pair_min}:</b> {min_price}\n"
                            f"{recomend_escaped}\n"
                            f"{stop_update}/stop_update"
                        )

                        await application.bot.send_message(chat_id=user['chat_id'],
                                                           text=message,
                                                           parse_mode='HTML')
                        # await application.bot.send_message(chat_id=user['chat_id'],
                        #                                    text=f"{recomend}\n"
                        #                                         f"{lang.STOP_UPDATE}/stop_update")
                        print(f"{user['username']} {user['trading_pair']} = {price} in {datetime.now()}")
                    except TimedOut as e:
                        print(f"{e} --------- error")

            except TelegramError as e:
                await update_status(user["username"], False)
                print(f"------------------------{e}----------------------\n{user['username']}")
        if count >= DAY_COUNT:
            count = 0
            await check_users_for_finsh_time()
        await asyncio.sleep(SLEEP_TIME)


async def stop_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await find_and_set_lang(update, context)
    lang = LANGUAGES[context.user_data['language']]

    try:
        await update_status(update.message.from_user.username, False)
        await update.message.reply_text(lang.UPDATE_WAS_STOPPED)
    except:
        print("___________error__________stop_update________")


async def set_bot_commands(application: Application, language: str) -> None:
    lang = LANGUAGES[language]
    # lang = 'en'

    commands = [
        BotCommand("start", lang.BOT_START),
        BotCommand("set_interval", lang.SET_INTERVAL),
        BotCommand("info_bot", lang.ABOUT_BOT),
        BotCommand("info_interval", lang.INTERVAL_WHAT_IS_IT),
        BotCommand("support", lang.SUPPORT),
    ]

    await application.bot.set_my_commands(commands)
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def on_startup(application: Application) -> None:
    # Set default language to Espan if not specified
    await set_bot_commands(application, DEFAULT_LANGUAGE)
    asyncio.create_task(update_loop(application))


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).post_init(on_startup).build()  # Change menu lang

    # application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_interval", set_interval))
    application.add_handler(CommandHandler("info_bot", info_bot))
    application.add_handler(CommandHandler("info_interval", info_interval))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("stop_update", stop_update))

    application.add_handler(CallbackQueryHandler(choose_language_callback, pattern='^choose_language$'))
    application.add_handler(CallbackQueryHandler(set_interval_callback, pattern='^set_interval$'))
    application.add_handler(CallbackQueryHandler(update_data, pattern='^newsletter$'))
    application.add_handler(CallbackQueryHandler(get_chart, pattern='^True$'))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(update_interval, pattern='^\d{5}$'))
    application.add_handler(CallbackQueryHandler(analisys, pattern='^[A-Z]{3,5}[A-Z]{3,5}$'))
    application.add_handler(CallbackQueryHandler(interval_choice))

    # обработчики команд админа
    application.add_handler(CommandHandler("add", add_command_admin))
    application.add_handler(CommandHandler("stop", stop_command_admin))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("u_info", u_info_admin))
    application.add_handler(CommandHandler("tr", transactions))
    application.add_handler(CommandHandler("del_user", del_user))
    application.add_handler(CommandHandler("del_all_operations", del_all_operations))
    application.add_handler(CommandHandler("lst", lst))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analisys))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interval_choice))

    retries = 5
    while retries > 0:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            break
        except NetworkError as e:
            print(f"NetworkError: {e}. Retrying in 5 seconds...")
            retries -= 1
            sleep(2)
        except RetryAfter as e:
            print(f"RetryAfter: {e}. Retrying in {e.retry_after} seconds...")
            sleep(e.retry_after)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break


if __name__ == "__main__":
    main()
