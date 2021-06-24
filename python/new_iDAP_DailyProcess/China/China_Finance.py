#############################################
# 網站名稱：中國新聞網
# 網址： http://www.chinanews.com/finance/
# 爬取類型： 財經
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql
import json


def WebCrawling():
    targetUrl = "http://channel.chinanews.com/cns/cjs/cj.shtml?pager={}&pagenum=20&t=7_52"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
    }

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    page = 0

    while(True):
        res = requests.get(targetUrl.format(page), headers=headers)
        res.encoding = 'utf-8'
        if res.status_code == 403:
            return
        if res.status_code == 200:
            res_content = res.text[17:-29]
            result_json = json.loads(res_content)
            news = result_json["docs"]
            for new in news:
                url = new["url"]
                title = new["title"]
                publishdate = new["pubtime"][0:10].replace('-', '')
                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    return

                creationdate = datetime.now()
                content = ''

                contentRes = requests.get(url)
                contentRes.encoding = 'utf-8'
                if contentRes.status_code == 200:
                    contentSoup = BeautifulSoup(contentRes.text, 'lxml')
                    content = contentSoup.select('div.left_zw')[0].text
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

    web = "中國新聞網"

    WebCrawling()
