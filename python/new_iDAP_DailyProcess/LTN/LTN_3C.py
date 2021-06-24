#############################################
# 網站名稱：自由時報電子報
# 網址： https://3c.ltn.com.tw/
# 爬取類型： 3C
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def WebCrawling():
    targetUrl = "https://3c.ltn.com.tw/new_news/{}"
    baseUrl = 'https://3c.ltn.com.tw/'
    page = 1

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    while(True):
        res = requests.get(targetUrl.format(page))
        res.encoding = 'utf-8'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            news = soup.select('li.list_box')
            if len(news) == 0:
                break

            for new in news:
                title = new.select('div > a:nth-child(2)')[0].text.strip()
                url = baseUrl + new.select('div > a:nth-child(2)')[0].get('href')
                creationdate = datetime.now()
                content = ''

                contentres = requests.get(url)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    soup = BeautifulSoup(contentres.text, 'lxml')
                    publishdate = soup.select('span.time')[0].text.strip().split(' ')[0].replace('/', '')

                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        return

                    contents = soup.select('div.text p:not(.appE1121):not(.before_ir):not(.after_ir)')
                    content = ' '.join([c.text.strip() for c in contents])
                    contentres.close()

                    # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
                    #             (web, title, content, publishdate, url, creationdate))
                    # cur.execute('commit')

                    print("============================================================")
                    print(publishdate, title, url, content, creationdate)
                    print("============================================================")

        res.close()
        page = page + 1

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = 'pc89600059495s'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "自由時報電子報"

    WebCrawling()
