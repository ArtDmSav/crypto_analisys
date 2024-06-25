# import sentry_sdk
import configparser
from pathlib import Path

# Absolut path
dir_path = Path.cwd()
path = Path(dir_path, 'config', 'config.ini')
config = configparser.ConfigParser()
config.read(path)

# Constants
BOT_TOKEN = config['Telegram']['bot_token']
BOT_USERNAME = config['Telegram']['bot_username']

BINANCE_API = config['Binance']['api_key']
# BINANCE_KEY = config['Binance']['secret_key']

WAIT_BF_DEL_CHART_PNG = 3
