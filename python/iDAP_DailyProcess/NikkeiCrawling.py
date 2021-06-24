import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import re
import dbconfig
def WebCrawling():
    web = "nikkei" #"日經中文網"
    days = 5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()

        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }

        themes = ['china', 'politicsaeconomy', 'industry',
                  'product', 'trend', 'columnviewpoint', 'career']
        subUrl = 'https://zh.cn.nikkei.com/{}.html?start={}'
        c=0
        for the in themes:
            flag = True
            for page in range(0, 210, 10):
                if flag is False:
                    break

                targetUrl = subUrl.format(the, page)
                res = requests.get(targetUrl, headers=header, verify=False)
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    news = soup.select('.newsContent02 > dt')
                    for new in news:
                        title = new.select('a')[0].text.strip()
                        url = new.select('a')[0].get('href').strip()

                        creationdate = datetime.now()
                        content = ''
                        publishdate = new.select('span.date')[0].text

                        publishdate = re.sub('\(|\)|\/', '', publishdate)

                        if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                            flag = False
                            break

                        contentres = requests.get(
                            url, headers=header, verify=False)
                        contentres.encoding = 'utf-8'
                        if contentres.status_code == 200:
                            c=c+1
                            contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                            contents = contentsoup.select('.newsText > p')
                            content = ''.join([c.text.strip() for c in contents])
                            cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                            cur.execute('commit')
        print('26.Nikkei ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception NikkeiCrawling:'+str(e))

if __name__ == "__main__":
    WebCrawling()