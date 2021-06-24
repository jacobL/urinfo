from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)


def WebCrawling():
    baseUrl = "http://english.chosun.com/"
    targetUrl = "http://english.chosun.com/svc/list_in/list.html?catid={}&pn={}"
    targetArr = ["1", "F", "2", "3", "4", "G"]
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    for t in targetArr:
        flag = True
        for page in range(0, 10):
            if flag is False:
                break
            res = requests.get(targetUrl.format(t, page), headers=header)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'lxml')
                news = soup.select('.list_item')
                for new in news:
                    publishdate = new.select('.date')[0].text[0:10].replace('/', '')
                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        flag = False
                        break

                    title = new.select('dt > a')[0].text
                    url = baseUrl + new.select('dt > a')[0].get('href').strip()
                    creationdate = datetime.now()

                    try:
                        contentRes = requests.get(url, timeout=5)
                        contentRes.encoding = 'utf-8'
                        if contentRes.status_code == 200:
                            contentSoup = BeautifulSoup(contentRes.text, 'lxml')

                            contents = contentSoup.select('#news_body_id > .par')
                            content = ''.join([c.text.strip() for c in contents])

    # =============================================================================
                            # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
                            #             (web, title, content, publishdate, url, creationdate))
                            # cur.execute('commit')
    # =============================================================================

                            print("============================================================")
                            print(publishdate, title, url, content, creationdate)
                            print("============================================================")
                    except requests.exceptions.RequestException as e:
                        print(e)

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = '10.55.23.101'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "朝鮮日報"

    WebCrawling()
