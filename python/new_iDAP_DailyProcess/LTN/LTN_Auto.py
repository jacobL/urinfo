#############################################
# 網站名稱：自由時報電子報
# 網址： https://auto.ltn.com.tw/
# 爬取類型： 汽車
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def WebCrawling():
    carDict = {
        '國內要聞': '2',
        '國際快訊': '3',
        '試駕報導': '4',
        '交通新聞': '43',
        '品牌動態': '44',
        '愛車知識': '7'
    }
    targetUrl = "https://auto.ltn.com.tw/list/{}/{}"

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    for key in carDict:
        page = 1
        flag = True
        while(flag):
            res = requests.get(targetUrl.format(carDict[key], page))
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'lxml')
                news = soup.select('div.newsunit2')

                if len(news) == 0:
                    flag = False
                    
                for new in news:
                    publishdate = new.select('span.h1dt')[0].text.strip().split(' ')[0].replace('/', '')
                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        flag = False
                        break

                    title = new.select('a.title')[0].text.strip()
                    url = new.select('a.title')[0].get('href')
                    creationdate = datetime.now()
                    content = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        soup = BeautifulSoup(contentres.text, 'lxml')

                        contents = soup.select('div.text p:not(.appE1121):not(.before_ir):not(.after_ir):not(.ph_bc)')
                        content = ' '.join([c.text.strip() for c in contents])
                        contentres.close()

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

    web = "自由時報電子報"

    WebCrawling()
