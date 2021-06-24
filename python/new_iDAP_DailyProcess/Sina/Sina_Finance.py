#############################################
# 網站名稱：新浪
# 網址： https://news.sina.com.cn/china/
# 爬取類型： 財經
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql
import json


def WebCrawling():
    targetUrl = "https://feed.sina.com.cn/api/roll/get?pageid=121&lid=1356&num=20&versionNumber=1.2.4&page={}&encode=utf-8&callback=feedCardJsonpCallback&_=1608859920688"

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    page = 1

    while(True):
        res = requests.get(targetUrl.format(page))
        res.encoding = 'utf-8'
        if res.status_code == 403:
            return
        if res.status_code == 200:
            res_content = res.text[26:-14]
            result_json = json.loads(res_content)
            news = result_json["result"]["data"]

            for new in news:
                publishdate = datetime.fromtimestamp(int(new['ctime'])).strftime('%Y%m%d')
                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    return

                url = new["url"]
                title = new["title"]

                creationdate = datetime.now()
                content = ''

                contentRes = requests.get(url)
                contentRes.encoding = 'utf-8'
                if contentRes.status_code == 200:
                    contentSoup = BeautifulSoup(contentRes.text, 'lxml')
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
