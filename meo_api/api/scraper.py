import logging
import re
import html
import pathlib
import requests
import urllib.parse
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from drivers.driver import get_driver

PRICE_LEVEL_LABELS = {
    '安価': 1,
    'お手頃': 2,
    '高級': 3,
    '贅沢': 4,
    '$': 1,
    '$$': 2,
    '$$$': 3,
    '$$$$': 4,
}


class Scraper:
    def __init__(self, key_words, latitude, longitude):
        self.key_words = key_words
        self.latitude = latitude
        self.longitude = longitude
        self.driver = get_driver()


    def scrape_places(self):
        search_url = f"https://www.google.co.jp/maps/search/{self.key_words}/@{self.latitude},{self.longitude},15z"
        self.driver.get(search_url)
        wait = WebDriverWait(self.driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, 'q')))
        search_box.send_keys(self.key_words + Keys.RETURN)
        sleep(5)

       
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        

        while True:
            places = []
            for i in range(1, 21):
                try:
                    place_data = self._scrape_place_data(i)
                    print('Place data:', place_data)
                    places.append(place_data)

                except NoSuchElementException:
                    break
            # Scroll down
            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # sleep(10)
            # new_height = self.driver.execute_script("return document.body.scrollHeight")
            # if new_height == last_height:
            #     break
            # last_height = new_height
 
            self.driver.execute_script("window.scrollBy(0, 200);")
            sleep(1)

            self.driver.quit()

            return places

    def _scrape_place_data(self, rank):
        data = {}

        try:
            self.driver.find_element(
                By.XPATH, f'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[{rank*2+1}]/div/a').click()
            sleep(5)  # Wait for the panel to open
        except NoSuchElementException as e:
            logging.error(f"Element not found:{e}")
        pass

        try:
            name_element = self.driver.find_element(
                By.XPATH, '//h1[@class="DUwDvf fontHeadlineLarge"]')
            data['name'] = name_element.text
            print(f"Name found: {data['name']}")
        except NoSuchElementException:
            print("Name not found")
            

        try:
            address_element = self.driver.find_element(
                By.XPATH, '//div[contains(@class, "Io6YTe") and contains(@class, "fontBodyMedium") and contains(@class, "kR99db")]')

            if address_element.text != '':
                data['address'] = address_element.text
            else:
                data['address'] = None
            print(f"Address found: {data['address']}")

        except NoSuchElementException:
            print("Address not found")
            pass

        try:
            url_element = self.driver.find_element(
                By.XPATH, '//a[@class="CsEnBe"]')
            if url_element.get_attribute('href').startswith('https://business.google.com'):
                print('Invalid URL found')
                data['url'] = None
            else:
                data['url'] = url_element.get_attribute('href')
                print(f"url found: {data['url']}")
        except NoSuchElementException:
            print('URL not found')
            data['url'] = None
            pass
        
    
        try:
            rating_element = self.driver.find_element(
                By.XPATH, '//div[contains(@class,"F7nice")]/span/span[@aria-hidden="true"]')
            if rating_element.text != '':
                data['rating'] = float(rating_element.text)
            else:
                data['rating'] = None
            print(f"rating found: {data['rating']}")
        except NoSuchElementException:
            print('Rating not found')
            pass

        try:
            rating_total_element = self.driver.find_element(
                By.XPATH, '//div[contains(@class,"F7nice")]/span[2]/span/span[@aria-label]')
            if rating_total_element.text != '':
                # extract only the numbers from the string
                data['rating_total'] = int(
                    ''.join(filter(str.isdigit, rating_total_element.text)))
            else:
                data['rating_total'] = None
            print(f"total rating found: {data['rating_total']}")

        except NoSuchElementException:
            pass


        try:
            price_level_element = self.driver.find_element(
                By.XPATH, '//span[contains(@aria-label,"料金")]')
            if price_level_element.text != '':
                price_level_str = price_level_element.text
                data['price_level'] = PRICE_LEVEL_LABELS.get(price_level_str, -1)
            else:
                data['price_level'] = None
            print(f"Price level found: {data['price_level']}")
        except NoSuchElementException:
            pass

        try:
            price_level_element = self.driver.find_element(
                By.XPATH, '//button[@class="DkEaL " and @jsaction="pane.rating.category"]')
            if price_level_element.text != '':
                data['category'] = price_level_element.text
            else:
                data['category'] = None
            print(f"Category: {data['category']}")
        except NoSuchElementException:
            pass

        # try:

        #  #Close the panel
        #     self.driver.back()
        #         # By.XPATH, '//button[@aria-label="Back"]').click()
        #     sleep(10)  # Wait for the panel to close
        # except NoSuchElementException:
        #     print(f"Error navigating back: {e}")
        #     pass
        return data
    
