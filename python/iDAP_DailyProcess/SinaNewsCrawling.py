import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import re


def WebCrawling():
    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    subUrl = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page={}'

    for page in range(1, 31):
        targetUrl = subUrl.format(page)
        res = requests.get(targetUrl, headers=header)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            result_json = res.json()
            news = result_json['result']['data']
            for new in news:
                title = new['title']
                url = new['url']
                print(url)
                creationdate = datetime.now()
                content = ''
                publishdate = ''

                contentres = requests.get(
                    url, headers=header)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    contents = contentsoup.select('.article > p')
                    if len(contents) == 0:
                        contents = contentsoup.select('#artibody > p')
                        publishdate = contentsoup.select('#pub_date')[0].text.strip().split(' ')[
                            0].replace('-', '')
                    else:
                        publishdate = contentsoup.select('.date-source > .date')[0].text.split(
                            ' ')[0].replace('年', '').replace('月', '').replace('日', '')

                    content = ''.join([c.text.strip() for c in contents])

                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        break

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

    web = "新浪網"

    WebCrawling()
