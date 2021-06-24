import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def WebCrawling():
    web = "worldjournal" #"世界新聞網"
    days = 5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()

        subUrl = 'https://www.worldjournal.com/api/more?type=breaknews&page={}'
        c=0
        for page in range(1, 20):

            targetUrl = subUrl.format(page)

            res = requests.get(targetUrl)
            res.encoding = 'utf-8'

            if res.status_code == 200:
                result_json = res.json()
                news = result_json['lists']
                for new in news:
                    title = new['title']
                    url = new['titleLink']
                    publishdate = new['time']['art_roc_time'].split(
                        ' ')[0].replace('-', '')

                    if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                        break

                    creationdate = datetime.now()
                    content = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        c=c+1
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        contents = contentsoup.select(
                            '.article-content__editor > p')
                        content = ''.join([c.text.strip() for c in contents])
                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)', (web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')
        print('24.WorldJournal ',creationdate,' total:',c) 
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception WorldJournalCrawling:'+str(e))
        print('24.WorldJournal ',creationdate,' total:',c)         
if __name__ == "__main__":
    WebCrawling()
