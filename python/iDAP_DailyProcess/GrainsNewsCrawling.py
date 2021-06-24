import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests


def WebCrawling():
    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    # 新聞中心 -> 台灣新聞
    targetUrl = 'https://grains.org.tw/taiwan_news/'
    res = requests.get(targetUrl)
    res.encoding = 'utf-8'
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'lxml')
        news = soup.select('.posts-container article')

        for new in news:
            title = new.select(
                '.article-content-wrap > .post-header > h3 > a')[0].text.strip()
            url = new.select(
                '.article-content-wrap > .post-header > h3 > a')[0].get('href').strip()

            creationdate = datetime.now()
            content = ''
            publishdate = new.select(
                '.article-content-wrap > .post-header > span')[0].text.strip().replace('-', '')

            if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                break

            contentres = requests.get(url)
            contentres.encoding = 'utf-8'
            if contentres.status_code == 200:
                contentsoup = BeautifulSoup(contentres.text, 'lxml')
                contents = contentsoup.select(
                    '.content-inner > p')
                content = ''.join([c.text for c in contents])

            print("==========================================================")
            print(publishdate, title, url, content, creationdate)
            print("==========================================================")

# =============================================================================
            # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
            #             (web, title, content, publishdate, url, creationdate))
            # cur.execute('commit')
# =============================================================================

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "美國穀物協會"

    WebCrawling()
