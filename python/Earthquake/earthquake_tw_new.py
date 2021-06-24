# 20210209 目前台灣地震的邏輯，已經改為 (1)影響城市AML(非震央)，且(2) 3級以上與(3)發生3天內。  符合以上3條件才紀錄

import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

host = '10.55.23.168'
port = 33060
user = 'root'
passwd = "1234"
db = 'idap'

conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
cur = conn.cursor()

cur.execute("SELECT city FROM aml_country_city WHERE country='台灣' order by SYSTEM_FACTORY_count desc")
cityList = [item[0] for item in cur.fetchall()]

archiveDate = 30
deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')

baseUrl = 'https://www.cwb.gov.tw'
url = 'https://www.cwb.gov.tw/V8/C/E/MOD/EQ_ROW.html'
res = requests.get(url)
res.encoding = 'utf-8'
contentsoup = BeautifulSoup(res.text, 'html.parser')
eList = contentsoup.select(".eq-infor > a")

cur.execute("delete FROM `earthquake_tw` WHERE DATE_FORMAT(datetime, '%Y%m%d') < "+deleteFromDate)
if len(eList) > 0 :

    for ear in eList :
        #print(ear.get('href'))
        earRes = requests.get(baseUrl+ear.get('href'))
        earRes.encoding = 'utf-8'
        earContent = BeautifulSoup(earRes.text, 'html.parser')
        info = earContent.select(".quake_info > li")
        index = earContent.select(".yellow-dot-title")[0].text.strip()

        if '號' in index :
            index = index.split('號')[0].replace('第','').strip()
        else :
            index = '小區域'
        #print('index:',index)
        datetime_str = info[0].text.strip().replace('發震時間：','')
        datetime_obj = datetime.strptime(datetime_str,'%Y/%m/%d %H:%M:%S')
        datetime_str = datetime.strftime(datetime_obj, '%Y%m%d')
        #region = info[1].text.strip().replace('位置：','').replace('\n                                ','，')
        detailList = earContent.select(".accordion-toggle")
        if len(detailList) and int(datetime_str) > int(deleteFromDate) > 0 :
            for detail in detailList :
                tmp = detail.text.strip().replace('縣地區最大震度','').replace('市地區最大震度','').replace('級','')
                region = tmp.split(' ')[0]
                mag = tmp.split(' ')[1]
                creationdate = datetime.now()
                #print(datetime_obj,' ',region,' ',mag)
                if (region in cityList and int(mag)>2 ) :
                    cur.execute("insert ignore into earthquake_tw(`index`,datetime,region,mag,creationdate) values(%s,%s,%s,%s,%s)",(index,datetime_obj,region,mag,creationdate))            
cur.execute("commit") 
cur.close()
conn.close()          