#############################################
# 網站名稱：ET TODAY
# 網址： https://finance.ettoday.net/focus/104
# 爬取類型： 財經最新
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
    web = "ETToday_Finance" 
    tag = "Finance"
    
    targetUrl = "https://finance.ettoday.net/focus/104/{}"
    page = 1
    lastPageDesc = ''
    
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
        cur = conn.cursor()
        c=0
        while(True):
            res = requests.get(targetUrl.format(page))
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')

                currentPageDesc = soup.select('#finance > div.wrapper_box > div > div.container_box > div > div > div.c1 > div.part_pager_1 > p')[0].text
                if lastPageDesc == currentPageDesc:
                    break

                news = soup.select('a.piece.clearfix')
                for new in news:
                    publishdate = new.select('p.date')[0].text.strip()
                    if '-' not in publishdate:
                        publishdate = datetime.now().strftime('%Y%m%d')
                    else:
                        publishdate = publishdate.split(' ')[0].replace('-', '')

                    if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):    
                        break

                    title = new.select('h3')[0].text.strip()
                    url = new.get('href')
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
            lastPageDesc = currentPageDesc

        cur.close()
        conn.close()
    except Exception as e:
        print('Exception ETToday_Finance:'+str(e))
    print('ETToday_Finance ',creationdate,' total:',c)

if __name__ == "__main__":
    WebCrawling()