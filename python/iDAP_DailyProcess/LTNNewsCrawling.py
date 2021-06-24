from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import pymysql


def WebCrawling():
    host = '10.55.23.101'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'
    web = "ltn" #"自由時報電子報"
    
    try:
        targetUrl = "https://news.ltn.com.tw/ajax/breakingnews/all/{}"
        datas = []

        conn = pymysql.connect(host=host, port=port,
                               user=user, passwd=passwd, db=db)
        cur = conn.cursor()

        for page in range(1, 26):
            res = requests.get(targetUrl.format(page))
            res.encoding = 'utf-8'
            if res.status_code == 200:
                result_json = res.json()
                datas.append(result_json['data'])
        c=0
        for idx, data in enumerate(datas):
            if idx == 0:
                for d in data:
                    c=c+1
                    title = d['title']
                    url = d['url']
                    publishdate = d['time']
                    if '-' not in publishdate:
                        publishdate = date.today().strftime("%Y%m%d")
                    else:
                        publishdate = datetime.strptime(
                            publishdate, "%Y-%m-%d %H:%M").strftime("%Y%m%d")

                    creationdate = datetime.now()

                    res = requests.get(url)
                    res.encoding = 'utf-8'
                    if res.status_code == 200:
                        #soup = BeautifulSoup(res.text, 'lxml')
                        soup = BeautifulSoup(res.text, 'html.parser')
                        
                        contents = soup.select('div.text p:not(.appE1121)')
                        content = ' '.join([c.text for c in contents])

                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)', (web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')

                        #print("============================================================")
                        #print(publishdate, title, url, content, creationdate)
                        #print('LTNNews ',publishdate, title)
                        #print("============================================================")
            else:
                for i in range((idx) * 20, (idx+1) * 20):
                    c=c+1
                    title = data[str(i)]['title']
                    url = data[str(i)]['url']
                    publishdate = data[str(i)]['time']
                    if '-' not in publishdate:
                        publishdate = date.today().strftime("%Y%m%d")
                    else:
                        publishdate = datetime.strptime(
                            publishdate, "%Y-%m-%d %H:%M").strftime("%Y%m%d")

                    creationdate = datetime.now()

                    res = requests.get(url)
                    res.encoding = 'utf-8'
                    if res.status_code == 200:
                        #soup = BeautifulSoup(res.text, 'lxml')
                        soup = BeautifulSoup(res.text, 'html.parser')
                        
                        contents = soup.select('div.text p:not(.appE1121)')
                        content = ' '.join([c.text for c in contents])

    # =============================================================================
                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',  (web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')
    # =============================================================================

                        #print("============================================================")
                        #print(publishdate, title, url, content, creationdate)
                        #print('LTNNews ',publishdate, title)
                        #print("============================================================")
        
        print('7.LTNNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception LTNNewsCrawling:'+str(e))

if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "自由時報電子報"

    WebCrawling()
