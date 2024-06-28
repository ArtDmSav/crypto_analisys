# import sentry_sdk
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
ADMIN_USERNAME = (config['Admin']['admin_1'], config['Admin']['admin_2'])
