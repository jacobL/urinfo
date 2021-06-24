import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig
def WebCrawling():
    web = "kyodonews" #"共同網"
    days = 5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()

        # themes = ['global_news', 'japan-china_relationship']
        themes = ['global_news', 'japan-china_relationship',
                  'japan_politics', 'economy_science', 'cat116', 'society', 'cat85', 'cat88', 'culture_entertainment_sports', 'premier_movement', 'tokyo', 'local_news']
        subUrl = 'https://tchina.kyodonews.net/news/{}?page={}'
        baseUrl = 'https://tchina.kyodonews.net'
        c=0
        for the in themes:
            flag = True
            for page in range(1, 2):
                if flag == False:
                    break

                targetUrl = subUrl.format(the, page)
                res = requests.get(targetUrl)
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    news = soup.select('#js-postListItems li')

                    if len(news) == 0:
                        break

                    for new in news:
                        title = new.select('a h3')[0].text.strip()
                        url = baseUrl + new.select('a')[0].get('href').strip()

                        creationdate = datetime.now()
                        content = ''
                        publishdateTmp = new.select('.time')[0].text.split(' - ')[0].strip()
                        publishdateY = publishdateTmp.split('年')[0].strip()
                        publishdateM = publishdateTmp.split('年')[1].strip().split('月')[0].strip()
                        if int(publishdateM) < 10 :
                            publishdateM = '0'+publishdateM
                        publishdateD = publishdateTmp.split('月')[1].replace('日', '').strip() 
                        if int(publishdateD) < 10 :
                            publishdateD = '0'+publishdateD
                        publishdate = publishdateY+publishdateM+publishdateD
                        #publishdate = new.select(
                        #    '.time')[0].text.split(' - ')[0].strip().replace(
                        #    '年 ', '').replace('月 ', '').replace('日', '')
                        #print(publishdateTmp,' publishdate:',publishdate)
                        if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                            flag = False
                            break

                        contentres = requests.get(url)
                        contentres.encoding = 'utf-8'
                        if contentres.status_code == 200:
                            contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                            content = contentsoup.select('.article-body')[0].text
                            c=c+1

                            cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                            cur.execute('commit')

        print('21.KyodoNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception KyodoNewsCrawling:'+str(e))

if __name__ == "__main__":
    WebCrawling()