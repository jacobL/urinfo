import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig
def WebCrawling():
    web = "epochtimes" #"大紀元"
    days = 5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }

        targetUrl = 'https://www.epochtimes.com/b5/instant-news.htm'

        res = requests.get(targetUrl, headers=header)
        res.encoding = 'utf-8'
        c=0
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            news = soup.select('.one_post')
            for new in news:
                title = new.select('.title > a')[0].text.strip()
                url = new.select('.title > a')[
                    0].get('href').strip()

                creationdate = datetime.now()
                content = ''
                publishdate = ''

                contentres = requests.get(url, headers=header)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                    contents = contentsoup.select('.post_content > p')
                    if len(contents) == 0:
                        contents = contentsoup.select('#artbody > p')
                    content = ''.join([c.text.strip() for c in contents])

                    publishdate = contentsoup.select('time')[0].get(
                        'datetime').strip().split('T')[0].replace('-', '')
                    if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                        break 
                    c=c+1    
                    cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                    cur.execute('commit')
        print('23.EpochTimes ',creationdate,' total:',c)    
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception EpochTimesCrawling:'+str(e))
        print('23.EpochTimes ',creationdate,' total:',c) 

if __name__ == "__main__":
    WebCrawling()