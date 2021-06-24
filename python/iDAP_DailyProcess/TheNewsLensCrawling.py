import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def WebCrawling():
    web = "thenewslens" #關鍵評論
    days = 5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }

        targetUrl = 'https://www.thenewslens.com/'
        baseUrl = 'https://www.thenewslens.com'

        res = requests.get(targetUrl, headers=header)
        res.encoding = 'utf-8'
        c=0
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser') 
            for page in range(1, 2):
                topicres = requests.get(
                    '{}/latest-article?page={}'.format(baseUrl, page), headers=header)
                topicres.encoding = 'utf-8'
                if topicres.status_code == 200:
                    topicsoup = BeautifulSoup(topicres.text, 'html.parser')                     
                    news = topicsoup.select('.list-container')
                    for new in news:
                        title = new.select(
                            '.title > a')[0].get('title').strip()
                        url = new.select(
                            '.title > a')[0].get('href').strip()
                        creationdate = datetime.now()
                        content = ''
                        publishdate = new.select(
                            '.info-content > .time')[0].text.strip().replace('/', '')
                        #print(title,' ',publishdate)
                        contentres = requests.get(url, headers=header)
                        contentres.encoding = 'utf-8'
                        if contentres.status_code == 200:
                            contentsoup = BeautifulSoup(
                                contentres.text, 'html.parser')
                            contents = contentsoup.select(
                                '.article-content > p')
                            content = ''.join([c.text.strip()
                                               for c in contents])

                        if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                            break
                        c=c+1
                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s,%s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')
                            
        print('17.TheNewsLens ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception TheNewsLensCrawling:'+str(e))

if __name__ == "__main__":
    WebCrawling()