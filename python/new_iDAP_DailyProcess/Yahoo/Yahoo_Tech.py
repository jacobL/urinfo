#############################################
# 網站名稱：Yahoo!奇摩
# 網址： https://tw.news.yahoo.com/technology
# 爬取類型： 科技
# 爬取範圍： 今日、昨日
#############################################

import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests


def WebCrawling():
    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    baseUrl = 'https://tw.news.yahoo.com'
    targetUrl = 'https://tw.news.yahoo.com/_td-news/api/resource/IndexDataService.getExternalMediaNewsList;count=10;loadMore=true;mrs=%7B%22size%22%3A%7B%22w%22%3A220%2C%22h%22%3A128%7D%7D;newsTab=technology;start={};tag=%5B%22yct%3A001000931%22%2C%22yct%3A001000742%22%2C%22ymedia%3Acategory%3D000000175%22%5D;usePrefetch=false?bkt=news-TW-zh-Hant-TW-def&device=desktop&ecma=modern&feature=oathPlayer%2CvideoDocking&intl=tw&lang=zh-Hant-TW&partner=none&prid=39gpe1dftjhh8&region=TW&site=news&tz=Asia%2FTaipei&ver=2.3.1550&returnMeta=true'

    records = 0
    while True:
        res = requests.get(targetUrl.format(records))
        res.encoding = 'utf-8'
        if res.status_code == 200:
            result_json = res.json()
            news = result_json['data']
            for new in news:

                publishdate = datetime.fromtimestamp(new['published_at']).strftime('%Y%m%d')
                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    return

                url = baseUrl + new['url']
                title = new['title']
                creationdate = datetime.now()
                content = ''

                contentres = requests.get(url)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    contents = contentsoup.select('.caas-body')
                    content = ' '.join([c.text.strip() for c in contents])

                    print("============================================================")
                    print(publishdate, title, url, content, creationdate)
                    print("============================================================")

                # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                # cur.execute('commit')
        res.close()
        records = records + 10

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = 'pc89600059495s'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "Yahoo!奇摩"

    WebCrawling()
