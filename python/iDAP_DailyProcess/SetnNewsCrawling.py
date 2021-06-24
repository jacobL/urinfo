import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests


def WebCrawling():
    conn = pymysql.connect(host=host, port=port,
                           user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    targetUrl = 'https://www.setn.com/ViewAll.aspx?p={}'
    baseUrl = 'https://www.setn.com'

    for page in range(1, 21):
        res = requests.get(targetUrl.format(page), headers=header)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            news = soup.select('.newsItems')

            for new in news:
                title = new.select('.view-li-title > a')[0].text.strip()
                url = new.select('.view-li-title > a')[
                    0].get('href').strip()
                tag = new.select('.newslabel-tab > a')[0].text.strip()

                if url.startswith('https') is False:
                    url = baseUrl + url

                creationdate = datetime.now()
                content = ''
                publishdate = ''

                contentres = requests.get(url, headers=header)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    if tag == '娛樂' or tag == '日韓' or tag == '音樂' or url.startswith('https://star.setn.com/'):
                        contents = contentsoup.select('.printdiv > p')
                        publishdate = contentsoup.select(
                            'time')[0].text.strip().split(' ')[0].replace('/', '')
                    elif tag == '女孩':
                        contents = contentsoup.select('.ckuse > p')
                        publishdate = contentsoup.select(
                            '.date-area')[0].text.strip().split(' ')[0].replace('/', '')
                    elif tag == '旅遊' or url.startswith('https://travel.setn.com/'):
                        contents = contentsoup.select('.ckuse > p')
                        publishdate = contentsoup.select(
                            '.date-area')[0].text.strip().split(' ')[0].replace('/', '')
                    else:
                        contents = contentsoup.select('#Content1 > p')
                        publishdate = contentsoup.select(
                            '.page-date')[0].text.strip().split(' ')[0].replace('/', '')

                    content = ''.join([c.text.strip() for c in contents])

                    if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        break

                    print(
                        "==========================================================")
                    print(publishdate, title, url, content, creationdate)
                    print(
                        "==========================================================")

    # =============================================================================
            # cur.execute('insert ignore into news(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',
            #             (web, title, content, publishdate, url, creationdate))
            # cur.execute('commit')
    # =============================================================================

    cur.close()
    conn.close()


if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "三立新聞網"

    WebCrawling()
