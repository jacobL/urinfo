from apscheduler.schedulers.blocking import BlockingScheduler

from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import pymysql

import warnings
warnings.filterwarnings("ignore")

# 20200928 
#import Apple_3C_Auto

# 202104
import NHKNewsCrawling,en_CNNCrawling,en_UNNewsCrawling,DWNewsCrawling,en_DWNewsCrawling
import dbconfig
#host = '10.55.23.101'
#port = 33060
#user = 'root'
#passwd = "1234"
#db = 'idap'


conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
cur = conn.cursor()
#cur.execute('delete from news_daily')
#cur.execute('commit')

"""
print('1.Apple_3C_Auto ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
Apple_3C_Auto.WebCrawling()
"""
print('1.NHKNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
NHKNewsCrawling.WebCrawling()
print('2.en_CNNCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
en_CNNCrawling.WebCrawling()
print('3.en_UNNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
en_UNNewsCrawling.WebCrawling()
print('4.DWNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
DWNewsCrawling.WebCrawling()
print('5.en_DWNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
en_DWNewsCrawling.WebCrawling()
print('finish ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
 