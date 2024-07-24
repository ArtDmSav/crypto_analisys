import configparser
from pathlib import Path

# Absolut path
dir_path = Path.cwd()
path = Path(dir_path, 'config', 'config.ini')
config = configparser.ConfigParser()
config.read(path)

# Constants
DB_PASSWORD = config['Database']['db_password']
DB_LOGIN = config['Database']['db_login']
DB_NAME = config['Database']['db_name']

BOT_TOKEN = config['Telegram']['bot_token']
BOT_USERNAME = config['Telegram']['bot_username']

BINANCE_API = config['Binance']['api_key']
# BINANCE_KEY = config['Binance']['secret_key']

WAIT_BF_DEL_CHART_PNG = 3  # second
ADMIN_USERNAME = (config['Admin']['admin_1'], config['Admin']['admin_2'], config['Admin']['admin_3'])

# Sentry

# sentry_sdk.init(
#     dsn=config['Sentry']['sentry_dsn'],
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )
