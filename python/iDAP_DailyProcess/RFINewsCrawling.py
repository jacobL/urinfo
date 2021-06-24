import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig

def WebCrawling():
    web = "rfi" #"法廣"
    days = 5
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
        cur = conn.cursor()
        themes = ['中華世界', '亞洲周刊', '今日經濟', '全球連線', '公民廣場', '公民論壇', '北美來鴻', '台北一周', '國際縱橫', '微言微語',
                  '文化藝術', '文化遺產', '明鏡書刊', '曼谷專欄', '東京專欄', '柏林飛鴻', '法國世界報', '法國報紙摘要', '法國思想長廊',
                  '法國文藝欣賞', '法國美食', '法國風光', '法國風土人情', '法語教學-parlez-vous-paris', '特別專題', '環境與發展',
                  '美國專欄', '要聞分析', '要聞解說', '觀察中國']

        subUrl = 'https://www.rfi.fr/tw/專欄檢索/{}/'
        #'https: // www.rfi.fr/tw/專欄檢索/{}/15/#pager/'
        baseUrl = 'https://www.rfi.fr'

        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        c=0
        for the in themes:
            flag = True
            for page in range(1, 11):
                if flag == False:
                    break
                if page > 1:
                    targetUrl = subUrl.format(the) + '{}/#pager/'.format(page)
                else:
                    targetUrl = subUrl.format(the)

                res = requests.get(targetUrl, headers=header)
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    news = soup.select('.o-layout-list__item')
                    for new in news:
                        
                        title = new.select(
                            '.m-item-list-article > a > .article__infos > .article__title ')[0].text.strip()
                        url = baseUrl + new.select(
                            '.m-item-list-article > a')[0].get('href').strip()

                        creationdate = datetime.now()
                        content = ''
                        publishdate = new.select(
                            '.article__infos > .article__metadata > .article__date > time')[0].get('datetime').split('T')[0].replace('-', '')

                        if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                            flag = False
                            break
                        
                        contentres = requests.get(url, headers=header)
                        contentres.encoding = 'utf-8'
                        if contentres.status_code == 200:
                            c=c+1
                            contentsoup = BeautifulSoup(contentres.text, 'html.parser')
                            intro = contentsoup.select('.t-content__chapo')[0].text
                            contents = contentsoup.select('.t-content__body > p')
                            content = intro + ''.join([c.text for c in contents])
                            cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s,%s, %s, %s)', (web, title, content, publishdate, url, creationdate))
                            cur.execute('commit')
                        
        print('15.Rfi ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception RFINewsCrawling.py:'+str(e))

if __name__ == "__main__":
    WebCrawling()