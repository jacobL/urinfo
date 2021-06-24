import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def WebCrawling():
    web = "technews"
    days=5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)

        cur = conn.cursor()

        baseUrl = 'https://technews.tw/category/component/display-c/'
        c=0
        page = 1
        while page < 20:
            if page > 1:
                targetUrl = '{}page/{}/'.format(baseUrl, page)
            else:
                targetUrl = baseUrl

            res = requests.get(targetUrl)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                #soup = BeautifulSoup(res.text, 'lxml')
                soup = BeautifulSoup(res.text, 'html.parser')
                
                news = soup.select('div.content')
                for new in news:
                    c=c+1
                    title = new.select('h1.entry-title')[0].text
                    url = new.select('h1.entry-title > a')[0].get('href')
                    dates = new.select('tr:nth-of-type(2) > td > span:nth-of-type(5)')[0].text.split(' ')
                    publishdate = dates[0] + dates[2] + dates[4]

                    if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                        print('11.TechNews ',creationdate,' total:',c)
                        return


                    creationdate = datetime.now()
                    content = ''

                    contentres = requests.get(url)
                    contentres.encoding = 'utf-8'
                    if contentres.status_code == 200:
                        #contentsoup = BeautifulSoup(contentres.text, 'lxml')
                        contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                        
                        content = contentsoup.select('div.indent')[0].text.strip()


                    #print("============================================================")
                    #print(publishdate, title, url, content, creationdate)
                    #print('TechNews ',publishdate, title)
                    #print("============================================================")

    # =============================================================================
                    cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                    cur.execute('commit')
    # =============================================================================

            page = page + 1

        
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception TechNewsCrawling:'+str(e))
    print('11.TechNews ',creationdate,' total:',c)    

def main():
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'
    web = "TechNews"
    WebCrawling()
    
if __name__ == "__main__":
    main()
