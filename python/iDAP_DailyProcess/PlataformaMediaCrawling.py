import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig
def WebCrawling():
    web = "plataformamedia" #"平台媒體"
    days = 5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }

        subUrl = 'https://www.plataformamedia.com/zh-hant/seccao/國際/page/{}/'
        c = 0
        for page in range(1, 21):
            targetUrl = subUrl.format(page)
            res = requests.get(targetUrl, headers=header)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')

                headerNew = soup.select('.saxon-post > div > div > div')[0]
                title = headerNew.select('h3')[0].text.strip()
                url = headerNew.select('h3 > a')[0].get('href').strip()

                creationdate = datetime.now()
                content = ''

                contentres = requests.get(url, headers=header)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                    content = contentsoup.select(
                        '.entry-content')[0].text
                    publishdate = contentsoup.select(
                        '.post-date')[0].text.strip()
                    if '-' in publishdate:
                        publishdate = publishdate.split(' - ')[1]

                    publishdate = datetime.strptime(
                        publishdate, "%d/%m/%Y").strftime('%Y%m%d')

                    if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                        break 
                    c=c+1    
                    cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                    cur.execute('commit')

                news = soup.select('.saxon-post > .saxon-post-details')
                for new in news:
                    title = new.select('h3')[0].text.strip()
                    url = new.select('h3 > a')[0].get('href').strip()

                    creationdate = datetime.now()
                    content = ''
                    publishdate = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        content = contentsoup.select(
                            '.entry-content')[0].text
                        publishdate = contentsoup.select(
                            '.post-date')[0].text.strip()
                        if '-' in publishdate:
                            publishdate = publishdate.split(' - ')[1]

                        publishdate = datetime.strptime(
                            publishdate, "%d/%m/%Y").strftime('%Y%m%d')

                        if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                            break
                        c=c+1
                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')
        print('22.PlataformaMedia ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception PlataformaMedia:'+str(e))

if __name__ == "__main__":
    WebCrawling()