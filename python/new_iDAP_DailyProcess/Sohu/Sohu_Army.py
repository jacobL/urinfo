#############################################
# 網站名稱：搜狐
# 網址： https://mil.sohu.com/
# 爬取類型： 軍事
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def WebCrawling():
    targetUrl = "https://mil.sohu.com/info?spm=smpc.mil-home.news-title.1.1608790206455f7vfE1d"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
    }
    catgory = ["domestic", "international"]

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    res = requests.get(targetUrl, headers=headers)
    res.encoding = 'utf-8'
    print(res.status_code)
    if res.status_code == 403:
        return
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'lxml')
        for c in catgory:
            news = soup.select("#{} > div > a.ImageCardItem".format(c))
            for new in news:
                ad = soup.select(".ad-tag")
                if len(ad) > 0:
                    continue
                title = new.select(".title")[0].text.strip()
                url = new.get('href').strip()
                if url == "":
                    continue

                url = "https:" + url
                creationdate = datetime.now()
                content = ''

                contentRes = requests.get(url, headers=headers)
                contentRes.encoding = 'utf-8'
                if contentRes.status_code == 200:
                    contentSoup = BeautifulSoup(contentRes.text, 'lxml')
                    publishdate = contentSoup.select('#news-time')[0].text[0:10].replace('-', '')
                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        continue

                    contents = contentSoup.select('article.article > p:not(.ql-align-center):not([data-role="editor-name"])') + contentSoup.select('div.hidden-content > p:not(.ql-align-center)')
                    content = ' '.join([c.text.strip() for c in contents])
                    content = content.replace("返回搜狐，查看更多", "")
                contentRes.close()

                # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
                #             (web, title, content, publishdate, url, creationdate))
                # cur.execute('commit')

                print("============================================================")
                print(publishdate, title, url, content, creationdate)
                print("============================================================")

    res.close()

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = 'pc89600059495s'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "搜狐"

    WebCrawling()
