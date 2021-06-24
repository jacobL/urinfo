import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig
def WebCrawling():
    web = "hket" #"香港經濟日報"
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()

        subUrl = 'https://inews.hket.com/sran001/%E5%85%A8%E9%83%A8?p={}'
        c=0
        for page in range(1, 21):
            targetUrl = subUrl.format(page)
            res = requests.get(targetUrl)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                news = soup.select('.listing-content-container')

                for new in news:
                    title = new.select('.listing-title > a')[0].text.strip()
                    url = new.select('.listing-title > a')[0].get('href').strip()
                    if url.startswith('/'):
                        url = 'https://inews.hket.com' + url

                    creationdate = datetime.now()
                    content = ''
                    publishdate = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        contents = contentsoup.select(
                            '.article-detail-content-container > p')

                        if len(contents) == 0:
                            continue
                        c=c+1
                        content = ''.join([c.text.strip() for c in contents])
                        publishdate = datetime.today().strftime('%Y%m%d')
                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')
        print('25.HKETNews ',creationdate,' total:',c)                
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception HKETNewsCrawling:'+str(e))

if __name__ == "__main__":
    WebCrawling()