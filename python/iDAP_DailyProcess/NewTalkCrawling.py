import pymysql
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)


def WebCrawling():
    web = "newtalk" #"Newtalk"
    days = 5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }

        for dt in daterange(date.today() - timedelta(days=1), date.today()):
            #print("[{}]".format(dt.strftime("%Y%m%d")))

            targetUrl = 'https://newtalk.tw/news/summary/{}#cal'.format(
                dt.strftime('%Y-%m-%d'))

            res = requests.get(targetUrl, headers=header)
            res.encoding = 'utf-8'
            c=0
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                news = soup.select('.news-list-item')
                for new in news:
                    title = new.select('.newsBox > .news_title')[0].text.strip()
                    url = new.select('.newsBox')[
                        0].get('href').strip()

                    creationdate = datetime.now()
                    content = ''
                    publishdate = ''

                    contentres = requests.get(url, headers=header)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        contents = contentsoup.select(
                            '.news-content> div:nth-of-type(2) > p')
                        content = ''.join([c.text.strip() for c in contents])

                        publishdate = contentsoup.select('.content_date')[
                            0].text.strip().split(' ')[1].replace('.', '')
                    if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                        break
                    c=c+1    
                    cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                    cur.execute('commit')
        print('20.NewTalk ',creationdate,' total:',c)            
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception NewTalkCrawling.py:'+str(e))

if __name__ == "__main__":
    WebCrawling()