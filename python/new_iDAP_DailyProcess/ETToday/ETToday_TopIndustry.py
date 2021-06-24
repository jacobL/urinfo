#############################################
# 網站名稱：ET TODAY
# 網址： https://finance.ettoday.net/focus/106
# 爬取類型： 頂尖企業
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pymysql
import requests


def WebCrawling():
    targetUrl = "https://finance.ettoday.net/focus/106/{}"
    page = 1
    lastPageDesc = ''

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    while(True):
        res = requests.get(targetUrl.format(page))
        res.encoding = 'utf-8'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')

            currentPageDesc = soup.select('#finance > div.wrapper_box > div > div.container_box > div > div > div.c1 > div.part_pager_1 > p')[0].text
            if lastPageDesc == currentPageDesc:
                break

            news = soup.select('a.piece.clearfix')
            for new in news:
                publishdate = new.select('p.date')[0].text.strip()
                if '-' not in publishdate:
                    publishdate = datetime.now().strftime('%Y%m%d')
                else:
                    publishdate = publishdate.split(' ')[0].replace('-', '')

                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    break

                title = new.select('h3')[0].text.strip()
                url = new.get('href')
                creationdate = datetime.now()
                content = ''

                contentres = requests.get(url)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    contents = contentsoup.select('div.story > p')

                    content = ' '.join([c.text.strip() for c in contents])
                
                contentres.close()
                # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
                #             (web, title, content, publishdate, url, creationdate))
                # cur.execute('commit')

                print("============================================================")
                print(publishdate, title, url, content, creationdate)
                print("============================================================")

        res.close()
        page += 1
        lastPageDesc = currentPageDesc

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = 'pc89600059495s'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "ET TODAY"

    WebCrawling()
