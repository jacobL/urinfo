#############################################
# 網站名稱：環球網
# 網址： https://tech.huanqiu.com/
# 爬取類型： 科技
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def WebCrawling():
    targetUrl = "https://tech.huanqiu.com/api/list?node=%22/e3pmh164r/e3pmh2hq8%22,%22/e3pmh164r/e3pmh33i9%22,%22/e3pmh164r/e3pmh356p%22,%22/e3pmh164r/e3pmh3dh4%22,%22/e3pmh164r/e3pmtlao3%22,%22/e3pmh164r/e3pmtm015%22,%22/e3pmh164r/e3pmtnh4j%22,%22/e3pmh164r/e3pn1fd3s%22,%22/e3pmh164r/e3pn46ri0%22,%22/e3pmh164r/e3pn4bn46%22,%22/e3pmh164r/e3pn4gh77%22,%22/e3pmh164r/e3pn4qlss%22,%22/e3pmh164r/e3pn6fo08%22,%22/e3pmh164r/e3ptqlvrg%22&offset={}&limit=20"
    baseUrl = "https://china.huanqiu.com/article/{}"

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    offset = 0
    while(True):
        res = requests.get(targetUrl.format(str(offset)))
        res.encoding = 'utf-8'
        if res.status_code != 200:
            return
        if res.status_code == 200:
            result_json = res.json()
            news = result_json['list']

            for new in news:
                url = baseUrl.format(new["aid"])
                title = new["title"]
                creationdate = datetime.now()
                content = ''
                contentRes = requests.get(url)
                contentRes.encoding = 'utf-8'
                if contentRes.status_code == 200:
                    contentSoup = BeautifulSoup(contentRes.text, 'lxml')
                    publishdate = contentSoup.select('.metadata-info > p.time')[0].text[0:10].replace('-', '')
                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        return
                    contents = contentSoup.select('article > section > p')
                    content = ' '.join([c.text.strip() for c in contents])

                    contentRes.close()

                    # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
                    #             (web, title, content, publishdate, url, creationdate))
                    # cur.execute('commit')

                    print("============================================================")
                    print(publishdate, title, url, content, creationdate)
                    print("============================================================")

        res.close()
        offset = offset + 20
    cur.close()
    conn.close()


if __name__ == "__main__":
    host = 'pc89600059495s'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "環球網"

    WebCrawling()
