import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def get_tradingview_screenshot(interval: str, trading_pair: str, time_stamp: str) -> None:
    try:
        # Настройка Selenium
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')
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
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
