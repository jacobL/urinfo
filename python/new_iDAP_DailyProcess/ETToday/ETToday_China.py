#############################################
# 網站名稱：ET TODAY
# 網址： https://www.ettoday.net/news/focus/%E5%A4%A7%E9%99%B8/
# 爬取類型： 大陸
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pymysql
import requests


def WebCrawling(days = 2):
    host = '10.55.23.101'
    port = 33060
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    passwd = "1234"
    db = 'idap'
    web = "ETToday_China" 
    tag = "China"
    
    targetUrl = "https://www.ettoday.net/show_roll.php"
    baseUrl = "https://www.ettoday.net/"
    page = 1
    
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
        cur = conn.cursor()
        c=0
        while(page <= 10):
            formData = {'offset': page, 'tPage': '2', 'tFile': '3.json', 'tOt': '0', 'tSi': '4', 'tAr': '0'}
            res = requests.post(targetUrl.format(page), data=formData)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')

                news = soup.select('div.piece.clearfix')
                for new in news:
                    publishdate = new.select('span.date')[0].text.strip()
                    if '-' not in publishdate:
                        publishdate = datetime.now().strftime('%Y%m%d')
                    elif '/' not in publishdate:
                        tdate = datetime.strptime(publishdate, "%m/%d %H:%M")
                        publishdate = tdate.strftime('%Y%m%d')
                    else:
                        publishdate = publishdate.split(' ')[0].replace('-', '')

                    if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):    
                        break

                    title = new.select('h3 > a')[0].get('title').strip()
                    url = baseUrl + new.select('h3 > a')[0].get('href').strip()
                    creationdate = datetime.now()
                    content = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        contents = contentsoup.select('div.story > p')
                        content = ' '.join([c.text.strip() for c in contents])
                        contentres.close()
                        cur.execute('select count(1) from news_daily where url=%s',(url))
                        if cur.fetchone()[0] == 0 :
                            cur.execute('insert ignore into news_daily(web, title, content, tag, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s, %s)', (web, title, content, tag, publishdate, url, creationdate))
                            cur.execute('commit')
                            c=c+1
            res.close()
            page += 1

        cur.close()
        conn.close()
    except Exception as e:
        print('Exception ETToday_China:'+str(e))
    print('ETToday_China ',creationdate,' total:',c)
if __name__ == "__main__":
    WebCrawling()