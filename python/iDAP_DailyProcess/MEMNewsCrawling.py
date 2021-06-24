from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pymysql


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)


def WebCrawling():
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'
    web = "mem" #"中华人民共和国应急管理部"
    
    try:
        targetUrl = "https://www.mem.gov.cn/xw/{}/index{}.shtml"
        targetArr = ['yjyw', 'bndt', 'gdyj', 'jyll', 'mtxx', 'zhsgxx']

        baseUrl = 'https://www.mem.gov.cn/xw/{}/'

        conn = pymysql.connect(host=host, port=port,
                               user=user, passwd=passwd, db=db)
        cur = conn.cursor()
        c=0
        for t in targetArr:
            page = 1
            isContinue = True
            while(isContinue):
                if page == 1:
                    res = requests.get(targetUrl.format(t, ''))
                else:
                    res = requests.get(targetUrl.format(t, '_' + str(page-1)))

                res.encoding = 'utf-8'
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    news = soup.select('div.cont ul li')
                    for new in news:
                        c=c+1
                        publishdate = new.select(
                            'span')[0].text[0:10].replace('-', '')
                        if publishdate < '20200801':
                            isContinue = False
                            break

                        title = new.select('a')[0].text[0:-16]
                        originUrl = new.select('a')[0].get('href')
                        if originUrl.startswith('./') == True:
                            url = originUrl.replace('./', baseUrl.format(t), 1)
                        else:
                            url = originUrl
                        creationdate = datetime.now()

                        try:
                            contentRes = requests.get(url, timeout=5)
                            contentRes.encoding = 'utf-8'
                            if contentRes.status_code == 200:
                                contentSoup = BeautifulSoup(
                                    contentRes.text, 'html.parser')
                                contents = contentSoup.select(
                                    'p.MsoNormal:not([align="center"])')
                                content = ' '.join([c.text for c in contents])

    # =============================================================================
                                cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)', (web, title, content, publishdate, url, creationdate))
                                cur.execute('commit')
    # =============================================================================

                                #print("============================================================")
                                #print(publishdate, title, url, content, creationdate)
                                #print('MEMNews ',publishdate, title)
                                #print("============================================================")
                        except requests.exceptions.RequestException as e:
                            print(e)

                page = page + 1
        print('8.MEMNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception MEMNewsCrawling:'+str(e))

if __name__ == "__main__":
    host = '10.55.52.98'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    web = "中华人民共和国应急管理部"

    WebCrawling()
