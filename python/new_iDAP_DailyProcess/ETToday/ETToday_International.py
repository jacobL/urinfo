#############################################
# 網站名稱：ET TODAY
# 網址： https://www.ettoday.net/news/focus/%E5%9C%8B%E9%9A%9B/
# 爬取類型： 國際
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pymysql
import requests


def WebCrawling():
    targetUrl = "https://www.ettoday.net/show_roll.php"
    baseUrl = "https://www.ettoday.net/"
    page = 1

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    while(page <= 20):
        formData = {'offset': page, 'tPage': '2', 'tFile': '2.json', 'tOt': '0', 'tSi': '4', 'tAr': '0'}
        res = requests.post(targetUrl.format(page), data=formData)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')

            news = soup.select('div.piece.clearfix')
            for new in news:
                publishdate = new.select('span.date')[0].text.strip()
                if '/' in publishdate:
                    tdate = datetime.strptime(publishdate, "%m/%d %H:%M")
                    publishdate = tdate.strftime('%Y%m%d')
                elif '-' not in publishdate:
                    publishdate = datetime.now().strftime('%Y%m%d')
                else:
                    publishdate = publishdate.split(' ')[0].replace('-', '')

                if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                    break

                title = new.select('h3 > a')[0].get('title').strip()
                url = baseUrl + new.select('h3 > a')[0].get('href').strip()
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
