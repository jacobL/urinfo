#############################################
# 網站名稱：自由時報電子報
# 網址： https://ec.ltn.com.tw/list/weeklybiz
# 爬取類型： 財經週報
# 爬取範圍： 今日、昨日
#############################################

from bs4 import BeautifulSoup
import requests
from datetime import date, datetime, timedelta
import pymysql


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)


def WebCrawling():
    targetUrl = "https://ec.ltn.com.tw/list_ajax/weeklybiz/{}/{}"
    page = 1
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
    }

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    for dt in daterange(date.today() - timedelta(days=1), date.today()):
        print("[{}]".format(dt.strftime("%Y%m%d")))
        flag = True

        while(flag):
            res = requests.get(targetUrl.format(dt.strftime("%Y%m%d"), page), headers=headers)
            res.encoding = 'utf-8'
            print(res.status_code)
            if res.status_code == 403:
                break
            if res.status_code == 200:
                news = res.json()
                if len(news) == 0:
                    flag = False

                for new in news:
                    publishdate = new['A_ViewTime']
                    publishdate = datetime.strptime(publishdate, "%Y/%m/%d %H:%M").strftime("%Y%m%d")

                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        flag = False
                        break

                    title = new['LTNA_Title']
                    url = new['url']

                    creationdate = datetime.now()

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        soup = BeautifulSoup(contentres.text, 'lxml')
                        contents = soup.select('div.text p:not(.appE1121):not(.before_ir):not(.after_ir)')
                        content = ' '.join([c.text.strip() for c in contents])
                        content = content.replace('一手掌握經濟脈動', '').replace('點我訂閱自由財經Youtube頻道', '').strip()
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
