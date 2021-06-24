import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def WebCrawling():    
    web = "crossing" #"換日線"
    days = 5
    creationdate = datetime.now()
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()

        subUrl = 'https://crossing.cw.com.tw/sub-channel/{}?page={}'
        n = 0
        for c in range(1, 18):
            flag = True
            for page in range(1, 15):
                if flag == False:
                    break

                targetUrl = subUrl.format(c, page)
                res = requests.get(targetUrl)
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    news = soup.select('.card.card--article')

                    if len(news) == 0:
                        break

                    for new in news:
                        title = new.select('h3')[0].text.strip()
                        url = new.select('h3 > a')[0].get('href').strip()

                        creationdate = datetime.now()
                        content = ''
                        publishdate = ''

                        contentres = requests.get(url)
                        contentres.encoding = 'utf-8'
                        if contentres.status_code == 200:
                            contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                            introduction = contentsoup.select(
                                '.main-introduction')[0].text
                            contents = contentsoup.select(
                                'article > .trackSection > p')
                            content = '{} {}'.format(
                                introduction, ''.join([c.text for c in contents]))
                            publishdate = contentsoup.select(
                                '.info__date')[0].text.strip().replace('/', '')

                            if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                                flag = False
                                break 
                            n = n + 1     
                            cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                            cur.execute('commit')
        print('18.Crossing ',creationdate,' total:',n)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception CrossingCrawling.py:'+str(e))

if __name__ == "__main__":
    WebCrawling()