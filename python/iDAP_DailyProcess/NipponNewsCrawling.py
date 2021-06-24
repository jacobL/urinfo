import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests


def WebCrawling():
    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    baseUrl = 'https://www.nippon.com/'
    subUrl = 'https://www.nippon.com/api/search/hk/latest/20/{}/'

    for page in range(1, 21):

        targetUrl = subUrl.format(page)

        res = requests.get(targetUrl)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            result_json = res.json()
            news = result_json['body']['dataList']
            for new in news:
                title = new['title']
                url = baseUrl + new['pub_url']
                publishdate = new['pub_date'].split('T')[0].replace('-', '')

                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    return

                creationdate = datetime.now()
                content = ''

                contentres = requests.get(url)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    content = contentsoup.select('.editArea')[0].text

                print("============================================================")
                print(publishdate, title, url, content, creationdate)
                print("============================================================")

    # =============================================================================
    #             cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
    #                         (web, title, content, publishdate, url, creationdate))
    #             cur.execute('commit')
    # =============================================================================

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "日本資料庫"

    WebCrawling()
