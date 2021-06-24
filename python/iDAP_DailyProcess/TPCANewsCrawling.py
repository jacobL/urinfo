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
    web = "tpca" #"台灣電路板協會"
    days=5
    try:
        conn = pymysql.connect(host=host, port=port,
                               user=user, passwd=passwd, db=db)
        cur = conn.cursor()

        baseUrl = 'https://www.tpca.org.tw'
        targetUrl = 'https://www.tpca.org.tw/Message/PagingItem'

        mid = ['112', '113', '114', '115', '116', '283']
        itemid = ['21', '22', '23', '24', '25', '70']
        c=0
        for item, m in zip(itemid, mid):
            page = 1
            while page < 3:
                formData = { 'ModelID': item, 'NowPage': page }
                res = requests.post(targetUrl, data=formData)
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    result_json = res.json()
                    news = result_json['rows']
                    for new in news:
                        c=c+1
                        title = new['Title']
                        publishdate = new['PublicshDate'].replace('/', '')
                        if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                            break
                        url = '{}/Message/MessageView?id={}&mid={}'.format(baseUrl, new['ItemID'], m)
                        creationdate = datetime.now()
                        content = ''

                        contentres = requests.get(url)
                        contentres.encoding = 'utf-8'
                        if contentres.status_code == 200:
                            #contentsoup = BeautifulSoup(contentres.text, 'lxml')
                            contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                            
                            content = contentsoup.select('div.content_con')[0].text

                        #print("============================================================")
                        #print(publishdate, title, url, content, creationdate)
                        #print('TPCANews ',publishdate, title)
                        #print("============================================================")

        # =============================================================================
                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')
        # =============================================================================

                page = page + 1

        print('13.TPCANews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception TPCANewsCrawling:'+str(e))

if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "台灣電路板協會"

    WebCrawling()
