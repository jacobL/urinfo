#############################################
# 網站名稱：聯合早報
# 網址： https://www.zaobao.com.sg/zfinance/realtime
# 爬取類型： 財經
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pymysql
import requests


def WebCrawling():
    targetUrl = "https://www.zaobao.com.sg/zfinance/realtime?page={}"
    baseUrl = "https://www.zaobao.com.sg"
    page = 0
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
    }

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    while(True):
        res = requests.get(targetUrl.format(page), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            return
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')

            news = soup.select('div.article-type')
            for new in news:
                publishdate = new.select('span.meta-published-date')[0].text.strip()
                if '/' not in publishdate:
                    publishdate = datetime.now().strftime('%Y%m%d')
                else:
                    tdate = datetime.strptime(publishdate, "%d/%m/%Y")
                    publishdate = tdate.strftime('%Y%m%d')

                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    return

                title = new.select('a.article-type-link > h2')[0].text.strip()
                url = baseUrl + new.select('a.article-type-img-link')[0].get('href').strip()
                creationdate = datetime.now()
                content = ''

                contentres = requests.get(url, headers=headers)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    contents = contentsoup.select('div.article-content-rawhtml > p')

                    content = ' '.join([c.text.strip() for c in contents])

                contentres.close()
                # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
                #             (web, title, content, publishdate, url, creationdate))
                # cur.execute('commit')

                print("============================================================")
                print(publishdate, title, url, content, creationdate)
                print("============================================================")

        res.close()
        page += 1

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = 'pc89600059495s'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "聯合早報"

    WebCrawling()
