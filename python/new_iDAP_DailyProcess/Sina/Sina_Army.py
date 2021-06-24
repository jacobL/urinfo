#############################################
# 網站名稱：新浪
# 網址： https://news.sina.com.cn/china/
# 爬取類型： 軍事
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql
import json


def WebCrawling():
    targetUrl = "http://mil.news.sina.com.cn/roll/index.d.html?cid={}&page={}"
    cid = ['57918', '57919']

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    for k in cid:
        page = 1
        flag = True
        while(flag):
            res = requests.get(targetUrl.format(k, page))
            res.encoding = 'utf-8'
            if res.status_code == 403:
                return
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'lxml')
                news = soup.select('ul.linkNews > li')

                for new in news:
                    url = new.select('a')[0].get('href').strip()
                    title = new.select('a')[0].text

                    creationdate = datetime.now()
                    content = ''

                    contentRes = requests.get(url)
                    contentRes.encoding = 'utf-8'
                    if contentRes.status_code == 200:
                        contentSoup = BeautifulSoup(contentRes.text, 'lxml')
                        publishdate = contentSoup.select('.date')[0].text[0:10].replace('年', '').replace('月', '').replace('日', '')
                        if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                            flag = False
                            break

                        contents = contentSoup.select('#article > p')
                        content = ' '.join([c.text.strip() for c in contents])
                    contentRes.close()

                    if content.strip() == "":
                        continue

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

    web = "新浪"

    WebCrawling()
