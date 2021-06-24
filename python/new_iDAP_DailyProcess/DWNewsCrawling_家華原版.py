from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)


def WebCrawling():
    baseUrl = "https://www.dw.com/"
    targetUrl = "https://www.dw.com/zh/在线报导/{}"
    targetArr = ["s-9058", "非常德国/s-101347", "时政风云/s-1681", "评论分析/s-100993"]
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    for t in targetArr:
        res = requests.get(targetUrl.format(t), headers=header)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            news = soup.select('.news')
            for new in news:

                title = new.select('a > h2')[0].text
                url = baseUrl + new.select('a')[0].get('href').strip()
                creationdate = datetime.now()

                try:
                    contentRes = requests.get(url, timeout=5)
                    contentRes.encoding = 'utf-8'
                    if contentRes.status_code == 200:
                        contentSoup = BeautifulSoup(contentRes.text, 'lxml')

                        publishdate = contentSoup.select('.smallList > li')[0].text.replace("日期", "").strip()
                        publishdate = datetime.strptime(publishdate, '%d.%m.%Y').strftime('%Y%m%d')
                        if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                            continue

                        bodyContent = contentSoup.select('#bodyContent')[0]
                        contents = bodyContent.select('p')
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

    web = "德國之聲"

    WebCrawling()
