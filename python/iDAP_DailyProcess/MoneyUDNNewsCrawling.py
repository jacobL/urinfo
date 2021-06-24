import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def WebCrawling():
    web = "udn" #"經濟日報"
    days=5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)

        cur = conn.cursor()

        baseUrl = 'https://money.udn.com/rank/newest/1001/0/{}'
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
            }

        c=0
        page = 1
        while page < 5:
            targetUrl = baseUrl.format(page)

            res = requests.get(targetUrl, headers=header)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                #soup = BeautifulSoup(res.text, 'lxml')
                soup = BeautifulSoup(res.text, 'html.parser')
                

                news = soup.select('table#ranking_table > tr')
                for idx, new in enumerate(news):
                    if idx == 0:
                        continue
                    c=c+1
                    title = new.select('td:nth-of-type(1)')[0].text
                    url = new.select('td:nth-of-type(1) > a')[0].get('href')

                    creationdate = datetime.now()
                    content = ''
                    publishdate = ''

                    contentres = requests.get(url, headers=header)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        #contentsoup = BeautifulSoup(contentres.text, 'lxml')
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        
                        content = contentsoup.select('div#article_body')[0].text.replace('推薦\n\n\n\n\n', '')
                        publishdate = contentsoup.select('.shareBar__info--author')[0].text[0:10].replace('-', '')

                        if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                            print('9.MoneyUDNNews ',creationdate,' total:',c)
                            return

                    #print("============================================================")
                    #print(publishdate, title, url, content, creationdate)
                    #print('MoneyUDNNews ',publishdate, title)
                    #print("============================================================")

    # =============================================================================
                    cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                    cur.execute('commit')
    # =============================================================================

            page = page + 1

        print('9.MoneyUDNNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception MoneyUDNNewsCrawling:'+str(e))
    #print('9.MoneyUDNNews ',creationdate,' total:',c)
if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "經濟日報"

    WebCrawling()
