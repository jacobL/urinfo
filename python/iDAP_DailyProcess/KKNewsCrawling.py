import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def WebCrawling():
    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    subUrl = 'https://kknews.cc/archive/{}/?page={}'

    browserOptions = webdriver.ChromeOptions()
    browserOptions.add_argument('--start-maximized')
    browserOptions.add_argument('headless')
    browserOptions.add_argument('log-level=3')

    getDriver = webdriver.Chrome(
        options=browserOptions, executable_path=r"chromedriver.exe")
    wait = WebDriverWait(getDriver, 180)
    wait_list = WebDriverWait(getDriver, 15)

    totalPage = 100
    getDriver.get(subUrl.format(datetime.today().strftime('%Y%m%d'), 1000))
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '#main-content > ul > li.page-numbers.current > a')))
    totalPage = getDriver.find_element_by_css_selector(
        '#main-content > ul > li.page-numbers.current > a').text

    for page in range(1, int(totalPage)):
        # time.sleep(random.randint(1, 10))
        targetUrl = subUrl.format(datetime.today().strftime('%Y%m%d'), page)
        time.sleep(random.randint(1, 10))
        getDriver.get(targetUrl)
        for i in range(1, 18):
            if i == 6 or i == 10:
                continue

            try:
                wait_list.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#main-content > article:nth-child({}) > div > header > h3 > a'.format(i))))
                title = getDriver.find_element_by_css_selector(
                    '#main-content > article:nth-child({}) > div > header > h3 > a'.format(i)).text.strip()

                url = getDriver.find_element_by_css_selector(
                    '#main-content > article:nth-child({}) > div > header > h3 > a'.format(i)).get_attribute('href').strip()

                creationdate = datetime.now()
                content = ''

                wait_list.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#main-content > article:nth-child({}) > div > header > p > a'.format(i))))
                publishdate = getDriver.find_element_by_css_selector(
                    '#main-content > article:nth-child({}) > div > header > p > a'.format(i)).text.strip().replace('-', '')

                if publishdate < datetime.today().strftime('%Y%m%d'):
                    break

                getDriver.execute_script("window.open('" + url + "');")

                # hadle new tab
                second_tab = getDriver.window_handles[1]
                # switch to second tab
                getDriver.switch_to.window(second_tab)

                wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#content > div > div.basic > p')))
                contents = getDriver.find_elements_by_css_selector(
                    '#content > div > div.basic > p')
                content = ' '.join([c.text.strip() for c in contents])

                print("==========================================================")
                print(publishdate, title, url, content, creationdate)
                print("==========================================================")

                getDriver.close()
                # switch to first tab
                getDriver.switch_to.window(getDriver.window_handles[0])

            finally:
                continue

        # =============================================================================
        # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
        #             (web, title, content, publishdate, url, creationdate))
        # cur.execute('commit')
        # =============================================================================

    print("===========================")
    print("finish")
    print("===========================")
    getDriver.quit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "每日頭條"

    WebCrawling()
