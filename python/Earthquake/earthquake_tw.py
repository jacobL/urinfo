import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

host = '10.55.23.101' 
port = 33060 
user = 'root'
passwd = "1234"
db = 'idap' 

conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
cur = conn.cursor()

archiveDate = 3
deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')

url = 'https://www.cwb.gov.tw/V8/C/E/MOD/MAP_LIST.html'
res = requests.get(url)
res.encoding = 'utf-8'
if res.status_code == 200:
    contentsoup = BeautifulSoup(res.text, 'html.parser')
    if len(contentsoup.select("a")) > 0 :
        cur.execute("delete from earthquake_tw")
        cur.execute("ALTER TABLE idap.earthquake_tw AUTO_INCREMENT = 1")
        print('delete all')
        for i in range(0,len(contentsoup.select("a"))):
            index = contentsoup.select("a")[i].text.split('，')[0]
            datetime_str = contentsoup.select("a")[i].text.split('，')[1].replace('時間為','')
            year='2021'
            if contentsoup.select("a")[i].text.split('，')[1].replace('時間為','')[0:2] == '12' :
                year='2020'
            datetime_obj = datetime.strptime(year+' '+datetime_str+'00', '%Y %m月%d日%H時%M%S')    
            datetime_str = datetime.strftime(datetime_obj, '%Y%m%d')
            if int(datetime_str) > int(deleteFromDate) :                  
                region = contentsoup.select("a")[i].text.split('，')[2]
                depth = contentsoup.select("a")[i].text.split('，')[3].replace('深度','').replace('公里','')
                mag = contentsoup.select("a")[i].text.split('，')[4].replace('地震規模','')[0:3]
                creationdate = datetime.now()
                cur.execute("insert into earthquake_tw(`index`,datetime,region,depth,mag,creationdate) values(%s,%s,%s,%s,%s,%s)",(index,datetime_obj,region,depth,mag,creationdate))            
        cur.execute("commit") 
        print('insert count:',len(contentsoup.select("a")))
cur.close()
conn.close()   