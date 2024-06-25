import ssl

import aiohttp
import pandas as pd
from tradingview_ta import Interval, TA_Handler

from config.data import BINANCE_API
from language import en, ru, tr, es

LANGUAGES = {
    'en': en,
    'ru': ru,
    'tr': tr,
    'es': es,
}


async def price_before_24h(trading_pair):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': trading_pair,
            'interval': '1h',
            'limit': 24
        }
        headers = {
            'X-MBX-APIKEY': BINANCE_API
        }
        try:
            async with session.get(url, headers=headers, params=params, ssl=False) as response:
                candles = await response.json()

            # Преобразование данных в DataFrame
            df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                                'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                                'taker_buy_quote_asset_volume', 'ignore'])

            # Преобразование типов данных
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)

            # Расчет максимальной и минимальной цены за 24 часа
            max_price = df['high'].max()
            min_price = df['low'].min()

            # Расчет изменения в процентах за 24 часа
            open_price = df['close'].iloc[0]
            close_price = df['close'].iloc[-1]
            price_change_percent = ((close_price - open_price) / open_price) * 100

            return max_price, min_price, round(price_change_percent, 2), close_price
        except Exception as e:
            print("error_price_before_24h = ", e)

            return 0, 0, 0, await tr_price(trading_pair)


async def tr_price(trading_pair):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={trading_pair}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                data = await response.json()
                print(data)
                print(data['price'])
                return data['price']
    except Exception as e:
        print(e)
        return ''


async def tr_view_bt(trading_pair, update, context) -> str:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]

    usr_interval = context.user_data.get("interval", Interval.INTERVAL_1_HOUR)
    show_usr_interval = context.user_data.get("show_usr_interval", lang.HOUR_1)

    try:
        response = TA_Handler(
            symbol=trading_pair,
            screener="crypto",
            exchange="BINANCE",
            interval=usr_interval
        )

        match response.get_analysis().summary["RECOMMENDATION"]:
            case 'BUY':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}" \
                       f"\n\n-------------------\n✅ {lang.BUY} ✅\n-------------------"
            case 'STRONG_BUY':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}" \
                       f"\n\n-------------------\n✅ {lang.STRONG_BUY} ✅\n-------------------"
            case 'SELL':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}" \
                       f"\n\n-------------------\n✅ {lang.SELL} ✅\n-------------------"
            case 'STRONG_SELL':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}" \
                       f"\n\n-------------------\n✅ {lang.STRONG_SELL} ✅\n-------------------"
            case 'NEUTRAL':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}" \
                       f"\n\n-------------------\n✅ {lang.NEUTRAL} ✅\n-------------------"
            case _:
                await update.callback_query.message.reply_text(lang.MSG_ERROR)
                return ''

    except Exception as e:
        await update.callback_query.message.reply_text(lang.REQUEST_ERROR)
        print(e)
        return ''


async def tr_view_msg(trading_pair, update, context) -> str:
    user_language = context.user_data.get('language', 'en')
    lang = LANGUAGES[user_language]

    usr_interval = context.user_data.get("interval", Interval.INTERVAL_1_HOUR)
    show_usr_interval = context.user_data.get("show_usr_interval", lang.HOUR_1)

    try:
        response = TA_Handler(
            symbol=trading_pair,
            screener="crypto",
            exchange="BINANCE",
            interval=usr_interval
        )

        match response.get_analysis().summary["RECOMMENDATION"]:
            case 'BUY':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.BUY}"
            case 'STRONG_BUY':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.STRONG_BUY}"
            case 'SELL':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.SELL}"
            case 'STRONG_SELL':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.STRONG_SELL}"
            case 'NEUTRAL':
                return f"{lang.BOT_RECOMMEND_1}{show_usr_interval}{lang.BOT_RECOMMEND_2}\n{lang.NEUTRAL}"
            case _:
                await update.message.reply_text(lang.MSG_ERROR)
                return ''

    except Exception as e:
        await update.message.reply_text(lang.REQUEST_ERROR)
        print(e)
        return ''
