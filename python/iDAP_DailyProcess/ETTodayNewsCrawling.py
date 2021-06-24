from bs4 import BeautifulSoup
import requests
from datetime import date, datetime, timedelta
import pymysql
import dbconfig
def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def WebCrawling(days=5):
    
    web = "ettoday" #"ET TODAY"
    
    try:
        targetUrl = "https://www.ettoday.net/show_roll.php"
        baseUrl = "https://www.ettoday.net"

        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)

        cur = conn.cursor()

        for dt in daterange(date.today() - timedelta(days=days), date.today()):
            #print("[{}]".format(dt.strftime("%Y%m%d")))
            c=0
            for page in range(1, 69):
                formData = {'offset': page, 'tPage': '3',
                            'tFile': '{}.xml'.format(dt.strftime("%Y%m%d"))}
                res = requests.post(targetUrl.format(page), data=formData)
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    #soup = BeautifulSoup(res.text, 'lxml')
                    soup = BeautifulSoup(res.text, 'html.parser')
                    
                    news = soup.select('h3')
                    for new in news:
                        
                        tag = new.select('em.tag')[0].text
                        publishdate = new.select('span.date')[
                            0].text[0:10].replace('/', '')
                        title = new.select('a')[0].text
                        relativeUrl = new.select('a')[0].get('href')
                        url = baseUrl + relativeUrl
                        creationdate = datetime.now()
                        content = ''

                        contentRes = requests.get(url)
                        contentRes.encoding = 'utf-8'
                        if contentRes.status_code == 200:
                            c=c+1
                            contentSoup = BeautifulSoup(contentRes.text, 'html.parser')
                            contents = contentSoup.select(
                                'div.story p:not(.no_margin)')
                            content = ' '.join([c.text for c in contents])

                            #cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)', (web, title, content, publishdate, url, creationdate))
                            cur.execute('insert into news_daily(web, title, content, publishdate, url, creationdate) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily WHERE url = %s) LIMIT 1',(web, title, content, publishdate, url, creationdate, url))
                            cur.execute('commit')
        print('6.ETTodayNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception ETTodayNewsCrawling:'+str(e))
    print('6.ETTodayNews ',creationdate,' total:',c)
if __name__ == "__main__":
    WebCrawling()
