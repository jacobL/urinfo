import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def WebCrawling(days=2):
    web = "yahoo" #"Yahoo!奇摩"
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()

        baseUrl = 'https://tw.news.yahoo.com'
        prefixUrl = 'https://tw.news.yahoo.com/_td-news/api/resource/IndexDataService.getExternalMediaNewsList;count=10;loadMore=true;mrs={"size":{"w":220,"h":128}};newsTab=all;start='
        c=0
        records = 0
        while True:
            tmpc=c
            targetUrl = prefixUrl + str(records) + ';tag=null;usePrefetch=false'
            res = requests.get(targetUrl)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                result_json = res.json()
                news = result_json
                for new in news:
                    c=c+1
                    title = new['title']
                    if "url" in new:
                        url = baseUrl + new['url']
                    else: 
                        continue

                    publishdate = datetime.fromtimestamp(new['published_at']).strftime('%Y%m%d')
                    if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                        print('14.YahooNews ',creationdate,' total:',c)    
                        return

                    creationdate = datetime.now()
                    content = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        #contentsoup = BeautifulSoup(contentres.text, 'lxml')
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        
                        contents = contentsoup.select('div.caas-body > p')

                        content = ' '.join([c.text for c in contents])


                    #print("============================================================")
                    #print(publishdate, title, url, content, creationdate)
                    #print('YahooNews ',publishdate, title)
                    #print("============================================================")


    # =============================================================================
                    cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                    cur.execute('commit')
    # =============================================================================
            if tmpc == c :
                print('14.YahooNews ',creationdate,' total:',c)
                return
            records = records + 10


        print('14.YahooNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception YahooNewsCrawling:'+str(e))

if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "Yahoo!奇摩"

    WebCrawling()
