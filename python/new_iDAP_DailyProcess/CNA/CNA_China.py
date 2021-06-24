#############################################
# 網站名稱：中央社
# 網址： https://www.cna.com.tw/list/acn.aspx
# 爬取類型： 兩岸
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def WebCrawling():
    targetUrl = "https://www.cna.com.tw/cna2018api/api/WNewsList"

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    for page in range(1, 5):
        formData = {'pageidx': page, 'pagesize': '20',
                    'action': '0', 'category': 'acn'}
        res = requests.post(targetUrl.format(page), data=formData)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            result_json = res.json()

            news = result_json['ResultData']['Items']

            for new in news:
                # tag = new["ClassName"]
                url = new["PageUrl"]
                title = new["HeadLine"]
                publishdate = new["CreateTime"][0:10].replace('/', '')
                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    return

                creationdate = datetime.now()
                content = ''

                contentRes = requests.get(url)
                contentRes.encoding = 'utf-8'
                if contentRes.status_code == 200:
                    contentSoup = BeautifulSoup(contentRes.text, 'lxml')
                    content = contentSoup.select('div.paragraph')[0].text

                    index = content.find('延伸閱讀')
                    if index > -1:
                        content = content[0: index]

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

    web = "中央社"

    WebCrawling()
