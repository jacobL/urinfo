#############################################
# 網站名稱：東森新聞網
# 網址： https://news.ebc.net.tw/news/car
# 爬取類型： 汽車
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def WebCrawling():
    targetUrl = "https://news.ebc.net.tw/realtime?page={}"
    baseUrl = "https://news.ebc.net.tw"

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    for page in range(1, 21):
        res = requests.post(targetUrl.format(page))
        res.encoding = 'utf-8'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            news = soup.select('div.style1.white-box:not(.list-ad)')
            for new in news:
                tag = new.select('.news-category')[0].text.strip()
                if tag != "汽車":
                    continue

                url = baseUrl + new.select('a')[0].get('href')

                title = new.select('a')[0].get('title')
                creationdate = datetime.now()

                publishdate = new.select('.small-gray-text')[0].text[0:5].replace('/', '')
                publishdate = str(datetime.now().year) + publishdate
                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    return

                content = ''

                contentres = requests.get(url)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    content = contentsoup.select('div.raw-style')[0].text.strip()

                    index = content.find('延伸閱讀')
                    if index < 0:
                        index = content.find('【往下看更多】')
                    content = content[0: index]

                    contents = content.split(' ')
                    content = ' '.join([c.strip() for c in contents])
                    contentres.close()

                    # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
                    #             (web, title, content, publishdate, url, creationdate))
                    # cur.execute('commit')

                    print("============================================================")
                    print(publishdate, title, url, content, creationdate)
                    print("============================================================")

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = 'pc89600059495s'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "東森新聞網"

    WebCrawling()
