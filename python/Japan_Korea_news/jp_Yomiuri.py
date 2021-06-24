from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.ie.options import Options
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pymysql
from datetime import datetime, timedelta
from google_trans_new import google_translator
import time
import random

from bs4 import BeautifulSoup
import requests 
host = '10.55.23.168'
port = 33060
user = 'root'
passwd = "1234"
db = 'idap'

 # 0:不呈現，1:呈現 debug mode
archiveDate = 10
web = 'yomiuri'
language = 'jp'
sleep_sec = 20
lang_src=language
lang_tgt='zh-tw'

def yomiuri_1(archiveDate = 10) :
    
    # 1.economy ###################################################
    baseUrl = 'https://www.yomiuri.co.jp/economy/'
    option = webdriver.ChromeOptions()
    option.add_argument("--test-type");
    option.add_argument("--disable-gpu");
    option.add_argument("--no-first-run");
    option.add_argument("--no-default-browser-check");
    option.add_argument("--ignore-certificate-errors");
    option.add_argument("--start-maximized");
    driver = webdriver.Chrome(r"D:\chromedriver.exe",chrome_options=option)
    driver.get(baseUrl)

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    tag = 'industry'

    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')

    #translator = google_translator()
    creationdate = datetime.now()

    # Part1 第1則
    if showPrintMSG :
        print("economy Part1")
    try : # 沒圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").get_attribute('href')
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").text
    except Exception as e : # 有圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[1]/h3/a").get_attribute('href')
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[1]/h3/a").text
    publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
    if int(publishdate) > int(deleteFromDate) :
        cur.execute('select count(1) from news_daily_source where url=%s',(url))
        if cur.fetchone()[0] == 0 :
            #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
            title_tw = gl_translator(title, lang_src, lang_tgt)
            cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
            cur.execute('commit')
            time.sleep(sleep_sec)   
            if showPrintMSG :
                print(1,title,title_tw,publishdate,url)    

    # Part1 第2~6則
    for i in range(2,7) :
        try : # 沒圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)    

    # Part2 第1~11則(沒有6)
    if showPrintMSG :
        print("economy Part2 第1~11則(沒有6)")
    for i in range(1,12) :
        if i == 6 :
            continue; 
        try : # 沒圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)
    cur.close()
    conn.close() 
    
    # 2.economy/global/  新聞較舊，幾乎沒有10天內。###################################################
    baseUrl = 'https://www.yomiuri.co.jp/economy/global/' 
    driver.get(baseUrl)
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    tag = 'industry'

    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')

    #translator = google_translator()
    creationdate = datetime.now()

    # Part1 第1則
    if showPrintMSG :
        print("economy/global Part1")
    try : # 沒圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").get_attribute('href')
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").text
    except Exception as e : # 有圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[2]/h3/a").get_attribute('href')
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[2]/h3/a").text
    publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
    if int(publishdate) > int(deleteFromDate) :
        cur.execute('select count(1) from news_daily_source where url=%s',(url))
        if cur.fetchone()[0] == 0 :
            #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
            title_tw = gl_translator(title, lang_src, lang_tgt)
            cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
            cur.execute('commit')
            time.sleep(sleep_sec) 
            if showPrintMSG :
                print(1,title,title_tw,publishdate,url) 

    # Part1 第2~5則
    for i in range(2,6) :
        try : # 沒圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)    

    # Part2 第1~21則 (沒有11)
    if showPrintMSG :
        print("\n economy/global Part2 第1~21則(沒有11)")
    for i in range(1,22) :   
        if i == 11 :
            continue;
        try : # 沒圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)
    cur.close()
    conn.close() 
    
    # 3.national ###################################################
    baseUrl = 'https://www.yomiuri.co.jp/national/'
    driver.get(baseUrl)

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    tag = 'national'

    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')

    #translator = google_translator()
    creationdate = datetime.now()

    # Part1 第1則
    if showPrintMSG :
        print("national Part1")
    try : # 沒圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").get_attribute('href')                                        
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").text
    except Exception as e : # 有圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[1]/h3/a").get_attribute('href')
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[1]/h3/a").text
    publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
    if int(publishdate) > int(deleteFromDate) :
        cur.execute('select count(1) from news_daily_source where url=%s',(url))
        if cur.fetchone()[0] == 0 :
            #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
            title_tw = gl_translator(title, lang_src, lang_tgt)
            cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
            cur.execute('commit')
            time.sleep(sleep_sec)   
            if showPrintMSG :
                print(1,title,title_tw,publishdate,url)    

    # Part1 第2~6則
    for i in range(2,7) :
        try : # 沒圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").get_attribute('href')                                            
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)   

    # Part2 第1~21則 (沒有11)
    if showPrintMSG :
        print("\n national Part2 第1~21則(沒有11)")
    for i in range(1,22) :   
        if i == 11 :
            continue;
        try : # 沒圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").get_attribute('href')                                            
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)     
    cur.close()
    conn.close() 
    
    # 4.international ###################################################

    baseUrl = 'https://www.yomiuri.co.jp/world/'
    driver.get(baseUrl)

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    tag = 'international'

    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')

    #translator = google_translator()
    creationdate = datetime.now()

    # Part1 第1則
    if showPrintMSG :
        print("international Part1")
    try : # 沒圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").get_attribute('href')
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").text
    except Exception as e : # 有圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[1]/h3/a").get_attribute('href')
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[1]/h3/a").text
    publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
    if int(publishdate) > int(deleteFromDate) :
        cur.execute('select count(1) from news_daily_source where url=%s',(url))
        if cur.fetchone()[0] == 0 :
            #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
            title_tw = gl_translator(title, lang_src, lang_tgt)
            cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
            cur.execute('commit')
            time.sleep(sleep_sec)   
            if showPrintMSG :
                print(1,title,title_tw,publishdate,url)    

    # Part1 第2~6則
    for i in range(2,7) :
        try : # 沒圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)    

    # Part2 第1~11則(沒有6)
    if showPrintMSG :
        print("international Part2 第1~11則(沒有6)")
    for i in range(1,12) :
        if i == 6 :
            continue; 
        try : # 沒圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)
    cur.close()
    conn.close()    
    
    # 5.tech  ###################################################
    baseUrl = 'https://www.yomiuri.co.jp/science/'
    driver.get(baseUrl)

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    tag = 'tech'

    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')

    #translator = google_translator()
    creationdate = datetime.now()

    # Part1 第1則
    if showPrintMSG :
        print("tech Part1")
    try : # 沒圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").get_attribute('href')                                        
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div/h3/a").text
    except Exception as e : # 有圖
        url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[1]/h3/a").get_attribute('href')
        title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li[1]/article/div/div[1]/h3/a").text
    publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
    if int(publishdate) > int(deleteFromDate) :
        cur.execute('select count(1) from news_daily_source where url=%s',(url))
        if cur.fetchone()[0] == 0 :
            #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
            title_tw = gl_translator(title, lang_src, lang_tgt)
            cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
            cur.execute('commit')
            time.sleep(sleep_sec)   
            if showPrintMSG :
                print(1,title,title_tw,publishdate,url)    

    # Part1 第2~6則
    for i in range(2,7) :
        try : # 沒圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").get_attribute('href')                                            
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("/html/body/div[9]/div[1]/div[1]/section/ul/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)   

    # Part2 第1~21則 (沒有11)
    if showPrintMSG :
        print("\n tech Part2 第1~21則(沒有11)")
    for i in range(1,22) :   
        if i == 11 :
            continue;
        try : # 沒圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").get_attribute('href')                                            
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div/h3/a").text
        except Exception as e : # 有圖
            url = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").get_attribute('href')
            title = driver.find_element_by_xpath("//*[@id='latest_list']/li["+str(i)+"]/article/div[1]/h3/a").text
        publishdate = url.split('/')[len(url.split('/'))-2].split('-')[0]
        if int(publishdate) > int(deleteFromDate) :
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                #title_tw = translator.translate(title,lang_src='jp', lang_tgt='zh-tw')
                title_tw = gl_translator(title, lang_src, lang_tgt)
                cur.execute('insert into news_daily_source(web, title, title_tw, publishdate, url, creationdate,language,tag) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily_source WHERE url = %s) LIMIT 1',(web, title, title_tw, publishdate, url, creationdate,language,tag, url))
                cur.execute('commit')
                time.sleep(sleep_sec) 
                if showPrintMSG :
                    print(i,title,title_tw,publishdate,url)  
    cur.close()
    conn.close()    
    driver.close()     
    
def yomiuri_2() :
    #translator = google_translator()
    
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    cur1 = conn.cursor()
    
    cur.execute('select count(1) from news_daily_source where status=0 and content is null and web="yomiuri" order by id')
    count = cur.fetchone()[0]
    if showPrintMSG :
        print('count for processing : ',count)
    if count > 0 :
        c=1
        cur.execute('select url from news_daily_source where status=0 and content is null and web="yomiuri" order by id')
        for r in cur :
            url = r[0]
            if showPrintMSG :
                print(c,'/',count,'. ',url)
            res = requests.get(url)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            content = soup.select(".p-main-contents")[0].text.replace('googletag.cmd.push(function() {','').replace('});','').replace("googletag.display('ad_dfp_premiumrec');",'').replace("\n", "").strip()
            content_tw = gl_translator(content, lang_src, lang_tgt)
            c = c + 1
            cur1.execute('update news_daily_source set content=%s,content_tw=%s where url=%s',(content,content_tw,url))
            cur1.execute('commit')
            if not showPrintMSG :
                time.sleep(sleep_sec)
                
def delete_old_data(archiveDate = 10) :
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()    
    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')
    cur.execute("delete from news_daily_source WHERE publishdate<=%s",(deleteFromDate))
    cur.execute("commit")

def gl_translator(text, lang_src, lang_tgt) :
    url_suffix_list = ['ac','ad','ae','al','am','as','at','az','ba','be','bf','bg','bi','bj','bs','bt','by','ca','cat','cc','cd','cf','cg','ch','ci','cl','cm','cn','co.ao','co.bw','co.ck','co.cr','co.id','co.il','co.in','co.jp','co.ke','co.kr','co.ls','co.ma','co.mz','co.nz','co.th','co.tz','co.ug','co.uk','co.uz','co.ve','co.vi','co.za','co.zm','co.zw','co','com.af','com.ag','com.ai','com.ar','com.au','com.bd','com.bh','com.bn','com.bo','com.br','com.bz','com.co','com.cu','com.cy','com.do','com.ec','com.eg','com.et','com.fj','com.gh','com.gi','com.gt','com.hk','com.jm','com.kh','com.kw','com.lb','com.lc','com.ly','com.mm','com.mt','com.mx','com.my','com.na','com.ng','com.ni','com.np','com.om','com.pa','com.pe','com.pg','com.ph','com.pk','com.pr','com.py','com.qa','com.sa','com.sb','com.sg','com.sl','com.sv','com.tj','com.tr','com.tw','com.ua','com.uy','com.vc','com.vn','com','cv','cx','cz','de','dj','dk','dm','dz','ee','es','eu','fi','fm','fr','ga','ge','gf','gg','gl','gm','gp','gr','gy','hn','hr','ht','hu','ie','im','io','iq','is','it','je','jo','kg','ki','kz','la','li','lk','lt','lu','lv','md','me','mg','mk','ml','mn','ms','mu','mv','mw','ne','nf','nl','no','nr','nu','pl','pn','ps','pt','ro','rs','ru','rw','sc','se','sh','si','sk','sm','sn','so','sr','st','td','tg','tk','tl','tm','tn','to','tt','us','vg','vu','ws']
    isSuccess = False
    url_suffix_inx = random.randint(0, len(url_suffix_list)-1)
    content_tw = ''
    while isSuccess == False :
        try :
            translator = google_translator(url_suffix=url_suffix_list[url_suffix_inx])        
            content_tw = translator.translate(text, lang_src=lang_src, lang_tgt=lang_tgt)
            isSuccess = True
        except Exception as e:
            url_suffix_inx = random.randint(0, len(url_suffix_list)-1)
    return content_tw

def yomiuri_etl(showPrintMSG = 0) :
    delete_old_data()
    yomiuri_1()
    yomiuri_2()    