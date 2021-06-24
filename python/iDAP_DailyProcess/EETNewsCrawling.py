import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests


def WebCrawling():
    host = '10.55.23.101'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'
    web = "eettaiwan" #"EET TAIWAN"
    
    try:
        conn = pymysql.connect(host=host, port=port,
                               user=user, passwd=passwd, db=db)
        cur = conn.cursor()

        baseUrl = 'https://www.eettaiwan.com/news/'

        page = 1
        c=0
        while page < 20:
            if page > 1:
                targetUrl = '{}page/{}/'.format(baseUrl, page)
            else:
                targetUrl = baseUrl

            res = requests.get(targetUrl)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                #soup = BeautifulSoup(res.text, 'lxml')
                soup = BeautifulSoup(res.text, 'html.parser')
                
                news = soup.select('div.post-description')
                for new in news:
                    c=c+1
                    title = new.select('h2')[0].text
                    url = new.select('h2 > a')[0].get('href')

                    creationdate = datetime.now()
                    content = ''
                    publishdate = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        #contentsoup = BeautifulSoup(contentres.text, 'lxml')
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        
                        contents = contentsoup.select('div.post-single > p')
                        content = ''.join([c.text for c in contents])
                        publishdate = contentsoup.select('.date')[0].text.replace('-', '')

                        if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                            print('5.EETNews ',creationdate,' total:',c)
                            return

                    #print("============================================================")
                    #print(publishdate, title, url, content, creationdate)
                    #print('EETNews ',publishdate, title)
                    #print("============================================================")

    # =============================================================================
                    cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                    cur.execute('commit')
    # =============================================================================

            page = page + 1

        print('5.EETNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception EETNewsCrawling:'+str(e))

if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "EET TAIWAN"

    WebCrawling()
