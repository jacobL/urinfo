#############################################
# 網站名稱：蘋果日報
# 網址： https://tw.appledaily.com/realtime/property/
# 爬取類型： 財經地產
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

    baseUrl = 'https://tw.appledaily.com'
    targetUrl = 'https://tw.appledaily.com/pf/api/v3/content/fetch/query-feed?query=%7B%22feedOffset%22%3A0%2C%22feedQuery%22%3A%22taxonomy.primary_section._id%3A%5C%22%2Frealtime%2Fproperty%5C%22%2BAND%2Btype%3Astory%2BAND%2Bdisplay_date%3A%5Bnow-200h%2Fh%2BTO%2Bnow%5D%2BAND%2BNOT%2Btaxonomy.tags.text.raw%3A_no_show_for_web%2BAND%2BNOT%2Btaxonomy.tags.text.raw%3A_nohkad%22%2C%22feedSize%22%3A100%2C%22sort%22%3A%22display_date%3Adesc%22%7D&d=180&_website=tw-appledaily'

    res = requests.get(targetUrl)
    res.encoding = 'utf-8'
    if res.status_code == 200:
        result_json = res.json()
        news = result_json['content_elements']
        for new in news:
            title = new['headlines']['basic']
            url = baseUrl + new['canonical_url']
            publishdate = new['display_date'][0:10].replace('-', '')
            if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                return

            creationdate = datetime.now()
            content = ''

            contentres = requests.get(url)
            contentres.encoding = 'utf-8'
            if contentres.status_code == 200:
                contentsoup = BeautifulSoup(contentres.text, 'lxml')
                content = contentsoup.select('div#articleBody')[0].text.strip()
                contentres.close()

            print("============================================================")
            print(publishdate, title, url, content, creationdate)
            print("============================================================")

            # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
            #             (web, title, content, publishdate, url, creationdate))
            # cur.execute('commit')

    res.close()
    cur.close()
    conn.close()


if __name__ == "__main__":
    host = 'pc89600059495s'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "蘋果日報"

    WebCrawling()
