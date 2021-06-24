from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pymysql


def WebCrawling():
    host = '10.55.23.101'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'
    web = "ebc" #"東森新聞網"
    
    try:
        targetUrl = "https://news.ebc.net.tw/realtime?page={}"
        baseUrl = "https://news.ebc.net.tw"

        conn = pymysql.connect(host=host, port=port,
                               user=user, passwd=passwd, db=db)
        cur = conn.cursor()

        c=0
        for page in range(1, 21):
            res = requests.post(targetUrl.format(page))
            res.encoding = 'utf-8'
            if res.status_code == 200:
                #soup = BeautifulSoup(res.text, 'lxml')
                soup = BeautifulSoup(res.text, 'html.parser')
                #news = soup.select('div.style1.white-box:not(.list-ad)')
                news = soup.select('div.style1.white-box')
                for new in news:
                    c=c+1
                    relativeUrl = new.select('a')[0].get('href')
                    if relativeUrl is None :
                        continue;
                    url = baseUrl + relativeUrl

                    title = new.select('a')[0].get('title')
                    creationdate = datetime.now()

                    publishdate = new.select('.small-gray-text')[0].text[0:5].replace('/', '')
                    publishdate = str(datetime.now().year) + publishdate

                    content = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        #contentsoup = BeautifulSoup(contentres.text, 'lxml')
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        
                        content = contentsoup.select('div.raw-style')[0].text

                        index = content.find('延伸閱讀')
                        if index < 0:
                            index = content.find('【往下看更多】')
                        content = content[0: index]


    # =============================================================================
                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')
    # =============================================================================

                        #print("============================================================")
                        #print(publishdate, title, url, content, creationdate)
                        #print('EBCNews ',publishdate, title)
                        #print("============================================================")
        print('3.EBCNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception EBCNewsCrawling:'+str(e))

if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "東森新聞網"

    WebCrawling()
