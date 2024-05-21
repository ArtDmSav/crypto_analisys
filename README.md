# Telegram Crypto Analysis Bot (EN/RU)

This is a multilingual Telegram bot that provides users with technical analysis of cryptocurrency pairs using the `tradingview_ta` library and data from Binance. The bot supports two languages: English and Russian. Users can select intervals for analysis and receive recommendations for buying, selling, or holding positions.

## Features

### Start Command (/start)
- Displays a welcome message and prompts the user to choose a language (English or Russian).
- Sets the default language to English and saves the user's choice.

### Language Selection
- Users can choose their preferred language via buttons.
- After selecting a language, the bot updates its commands and interface messages accordingly.

### Set Interval Command (/set_interval)
- Users can select an interval for analysis (1 minute, 5 minutes, 15 minutes, 30 minutes, 1 hour, 2 hours, 4 hours, 1 day, 1 week, 1 month).
- Saves the selected interval and displays the current value.

### Bot Information Command (/info_bot)
- Sends information about the bot's capabilities to the user.

### Interval Information Command (/info_interval)
- Explains the significance of intervals and their impact on data analysis.

### Cryptocurrency Pair Analysis
- Users enter the symbol of a cryptocurrency pair (e.g., BTCUSDT).
- The bot fetches the current price of the pair from Binance and performs technical analysis using the `tradingview_ta` library.
- Sends the current price and recommendations for buying, selling, or holding the position to the user.

## Logging
- The program uses the `logging` library to log events and errors.

## Asynchronous Execution
- Uses the `aiohttp` library for asynchronous HTTP requests to the Binance API.
- All request handling is performed asynchronously to ensure high performance and quick response times.

## Key Libraries and Technologies

1. **python-telegram-bot** - A library for building Telegram bots.
2. **tradingview_ta** - A library for fetching technical analysis from TradingView.
3. **aiohttp** - A library for performing asynchronous HTTP requests.
4. **logging** - A library for logging.

## Program Structure

- **config/data.py** - Contains the bot token.
- **db/commit.py** - Functions for recording user data and requests in the database.
- **db/create.py** - Function which create db and tables.
- **language/ru.py** - File with Russian text strings.
- **language/en.py** - File with English text strings.
- **Main file (bot.py)** - The main program file containing all command and message handlers, as well as functions for asynchronous execution and logging.

## How to Run

1. Clone the repository.
2. Install the required libraries.
3. Set up your bot token in `config/data.py`.
4. Run the bot using `python bot.py`.


_____________________________________________________________________________


# Telegram Crypto Analysis Bot

Это многоязычный бот для Telegram, который предоставляет пользователям технический анализ криптовалютных пар с использованием библиотеки `tradingview_ta` и данных с Binance. Бот поддерживает два языка: английский и русский. Пользователи могут выбирать интервалы для анализа и получать рекомендации по покупке, продаже или удержанию позиций.

## Функции

### Команда /start
- Отображает приветственное сообщение и предлагает пользователю выбрать язык (английский или русский).
- Устанавливает язык по умолчанию (английский) и сохраняет выбор пользователя.

### Выбор языка
- Пользователи могут выбрать предпочитаемый язык с помощью кнопок.
- После выбора языка бот обновляет команды и сообщения интерфейса на выбранный язык.

### Команда /set_interval
- Пользователь может выбрать интервал для анализа (1 минута, 5 минут, 15 минут, 30 минут, 1 час, 2 часа, 4 часа, 1 день, 1 неделя, 1 месяц).
- Сохраняет выбранный интервал и отображает текущее значение.

### Команда /info_bot
- Отправляет пользователю информацию о возможностях бота.

### Команда /info_interval
- Объясняет значение интервалов и их влияние на анализ данных.

### Анализ криптовалютной пары
- Пользователь вводит символ криптовалютной пары (например, BTCUSDT).
- Бот запрашивает текущую стоимость пары с Binance и проводит технический анализ с использованием библиотеки `tradingview_ta`.
- Отправляет пользователю текущую цену и рекомендации по покупке, продаже или удержанию позиции.

## Логирование
- Программа использует библиотеку `logging` для ведения логов событий и ошибок.

## Асинхронное выполнение
- Использует библиотеку `aiohttp` для выполнения асинхронных HTTP-запросов к API Binance.
- Вся обработка запросов выполняется асинхронно для обеспечения высокой производительности и быстрого ответа.

## Основные библиотеки и технологии

1. **python-telegram-bot** - Библиотека для создания ботов в Telegram.
2. **tradingview_ta** - Библиотека для получения технического анализа с TradingView.
3. **aiohttp** - Библиотека для выполнения асинхронных HTTP-запросов.
4. **logging** - Библиотека для ведения логов.

## Структура программы

- **config/data.py** - Содержит токен для доступа к боту.
- **db/commit.py** - Функции для записи данных пользователя и его запросов в базу данных.
- **db/create.py** - Функция для создания БД и таблиц.
- **language/ru.py** - Файл с русскими текстовыми строками.
- **language/en.py** - Файл с английскими текстовыми строками.
- **Основной файл (bot.py)** - Основной файл программы, содержащий все обработчики команд и сообщений, а также функции для асинхронного выполнения и логирования.

## Как запустить

1. Клонируйте репозиторий.
2. Установите необходимые библиотеки.
3. Настройте токен вашего бота в `config/data.py`.
4. Запустите бота с помощью команды `python bot.py`.

---

Это описание предоставляет полное представление о функциональности и структуре бота, подходящее для файла `README.md` на GitHub.


---

This description provides a comprehensive overview of the bot's functionality and structure, suitable for a `README.md` file on GitHub.
