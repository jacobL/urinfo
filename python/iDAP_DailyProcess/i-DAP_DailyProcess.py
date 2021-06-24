from apscheduler.schedulers.blocking import BlockingScheduler

from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import pymysql

import warnings
warnings.filterwarnings("ignore")

# 20200928 
import AppleNewsCrawling, CNANewsCrawling, EBCNewsCrawling,EDNNewsCrawling,EETNewsCrawling
import ETTodayNewsCrawling,LTNNewsCrawling,MEMNewsCrawling,MoneyUDNNewsCrawling#,NHKNewsCrawling
import TechNewsCrawling,TouTiaoNewsCrawling,TPCANewsCrawling,YahooNewsCrawling

import RFINewsCrawling,StormNewsCrawling,TheNewsLensCrawling,CrossingCrawling,NewTalkCrawling,KyodoNewsCrawling,PlataformaMediaCrawling,EpochTimesCrawling,WorldJournalCrawling,HKETNewsCrawling,NikkeiCrawling
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


print('1.AppleNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
AppleNewsCrawling.WebCrawling()

#print('2.CNANewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
#CNANewsCrawling.WebCrawling()

#print('3.EBCNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
#EBCNewsCrawling.WebCrawling()
#print('4.EDNNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
#EDNNewsCrawling.WebCrawling()
#print('5.EETNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
#EETNewsCrawling.WebCrawling()

print('6.ETTodayNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
ETTodayNewsCrawling.WebCrawling()

#print('7.LTNNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
#LTNNewsCrawling.WebCrawling()
print('9.MoneyUDNNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
#MEMNewsCrawling.WebCrawling()
MoneyUDNNewsCrawling.WebCrawling()
#print('10.NHKNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
#NHKNewsCrawling.WebCrawling()
print('11.TechNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
TechNewsCrawling.WebCrawling()
print('12.TouTiaoNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
TouTiaoNewsCrawling.WebCrawling()
#print('13.TPCANewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
#TPCANewsCrawling.WebCrawling()
print('14.YahooNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
YahooNewsCrawling.WebCrawling()


print('15.RFINewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
RFINewsCrawling.WebCrawling()

print('16.StormNewsCrawling ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
StormNewsCrawling.WebCrawling()

print('17.TheNewsLensCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
TheNewsLensCrawling.WebCrawling()
 
print('18.CrossingCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
CrossingCrawling.WebCrawling()
 
#print('19. ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
 
print('20.NewTalkCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
NewTalkCrawling.WebCrawling()

print('21.KyodoNewsCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
KyodoNewsCrawling.WebCrawling()

print('22.PlataformaMediaCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
PlataformaMediaCrawling.WebCrawling()

print('23.EpochTimesCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
EpochTimesCrawling.WebCrawling()

print('24.WorldJournalCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
WorldJournalCrawling.WebCrawling()

print('25.HKETNewsCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
HKETNewsCrawling.WebCrawling() 

print('26.NikkeiCrawling',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
NikkeiCrawling.WebCrawling()


print('finish ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
 
