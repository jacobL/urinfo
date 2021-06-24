import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def WebCrawling(days=2):
    web = "toutiao"
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)

        cur = conn.cursor()

        baseUrl = 'https://www.toutiao.com'
        targetUrl = 'https://www.toutiao.com/api/pc/feed/'

        param = {
            'max_behot_time': '0',
            'category': '__all__'
        }

        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        c=0
        records = 0
        res = requests.get(targetUrl, headers=header, params=param)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            result_json = res.json()
            news = result_json['data']
            for new in news:
                c=c+1
                title = new['title']
                url = '{}{}'.format(baseUrl, new['source_url'])

                publishdate = datetime.fromtimestamp(new['behot_time']).strftime('%Y%m%d')
                if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                    return

                creationdate = datetime.now()
                content = ''

                contentres = requests.get(url, headers=header)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    #contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                    
                    contents = contentsoup.select('article > p')
                    content = ' '.join([c.text.strip() for c in contents])


                #print("============================================================")
                #print(publishdate, title, url, content, creationdate)
                #print('TouTiaoNews ',publishdate, title)
                #print("============================================================")


    # =============================================================================
                cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                cur.execute('commit')
    # =============================================================================

            records = records + 10


        print('12.TouTiaoNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception TouTiaoNewsCrawling:'+str(e))

if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "今日頭條"

    WebCrawling()
