from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
# chrome_options.add_argument("--headless")

DRIVER_PATH = ChromeDriverManager(path='drivers').install()


def get_driver():
    driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
    print('driver is:', driver.title)
    return driver
