#############################################
# 網站名稱：搜狐
# 網址： https://business.sohu.com/category/macrography
# 爬取類型： 財經宏觀
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql
import json


def WebCrawling():
    targetUrl = "https://v2.sohu.com/integration-api/mix/region/6732?size=25&adapter=pc&secureScore=50&page={}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
    }

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    page = 1

    while(True):
        res = requests.get(targetUrl.format(page), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 403:
            return
        if res.status_code == 200:
            result_json = json.loads(res.text)
            news = result_json["data"]
            for new in news:
                if "url" not in new:
                    continue

                url = "https:" + new["url"]
                title = new["title"]

                creationdate = datetime.now()
                content = ''

                contentRes = requests.get(url, headers=headers)
                contentRes.encoding = 'utf-8'
                if contentRes.status_code == 200:
                    contentSoup = BeautifulSoup(contentRes.text, 'lxml')
                    publishdate = contentSoup.select('#news-time')[0].text[0:10].replace('-', '')
                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        return

                    contents = contentSoup.select('article.article > p:not(.ql-align-center)') + contentSoup.select('div.hidden-content > p:not(.ql-align-center)')
                    content = ' '.join([c.text.strip() for c in contents])                    
                contentRes.close()

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

    web = "搜狐"

    WebCrawling()
