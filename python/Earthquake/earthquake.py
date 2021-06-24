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

url = 'https://www.emsc-csem.org/#2w'
res = requests.get(url)
res.encoding = 'utf-8'
if res.status_code == 200:
    contentsoup = BeautifulSoup(res.text, 'html.parser')    
    #for i in range(0,len(contentsoup.select("#tbody > tr"))) :
    for i in range(len(contentsoup.select("#tbody > tr")),-1,-1) : 
        #print(i+1)
        try:                    
            datetime_str = contentsoup.select("#tbody > tr > .tabev6  a")[i].text.strip().replace('\xa0\xa0\xa0',' ').split(".")[0]
            datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            # GMT to TW zone
            datetime_object = datetime_object+timedelta(hours = 8)
            
            latitude = float(contentsoup.select("#tbody > tr > .tabev1")[i*2].text.strip())
            NS = contentsoup.select("#tbody > tr > .tabev2")[i*3].text.strip()
            if NS == 'S' :
                latitude = -1*latitude

            longitude = float(contentsoup.select("#tbody > tr > .tabev1")[i*2+1].text.strip())
            EW = contentsoup.select("#tbody > tr > .tabev2")[i*3+1].text.strip()
            if EW == 'W' : 
                longitude = -1*longitude

            depth = contentsoup.select("#tbody > tr > .tabev3")[i].text.strip()
            mag = contentsoup.select("#tbody > tr > .tabev2")[i*3+2].text.strip()
            region = contentsoup.select("#tbody > tr > .tb_region")[i].text.strip()
            creationdate = datetime.now()
            #print(datetime_object,' ',latitude,' ',longitude,' ',depth,' ',mag,' ',region)
            cur.execute("select count(1) from earthquake where datetime=%s and region=%s",(datetime_object,region))
            if cur.fetchone()[0] == 0:            
                cur.execute("insert into earthquake(datetime,latitude,longitude,depth,mag,region,creationdate) values(%s,%s,%s,%s,%s,%s,%s)",(datetime_object,latitude,longitude,depth,mag,region,creationdate))            
                cur.execute("commit") 
        except Exception as e:
            print('Exception earthquake:'+str(e))
cur.close()
conn.close()            