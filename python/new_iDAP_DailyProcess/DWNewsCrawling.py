from bs4 import BeautifulSoup
import requests
import pymysql
from datetime import datetime, timedelta,timezone  
import opencc 
import dbconfig

def WebCrawling():
    host = '10.55.23.101'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'

    showPrintMSG = 1 # 0:不呈現，1:呈現 debug mode
    archiveDate = 10
    web = 'dw' 
    sleep_sec = 2 
    
    baseUrl = "https://www.dw.com/"
    targetUrl = "https://www.dw.com/zh/在线报导/{}"
    targetArr = ["s-9058", "非常德国/s-101347", "时政风云/s-1681", "评论分析/s-100993", "经济纵横/s-1682", "科技环境/s-1686"]
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
    cur = conn.cursor()
    cc = opencc.OpenCC('s2t')
    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')
    tag = 'industry'
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    creationdate = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')
    c = 0
    for t in targetArr:
        res = requests.get(targetUrl.format(t), headers=header)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            news = soup.select('.news')
            for new in news:

                title = cc.convert(new.select('a > h2')[0].text)
                url = baseUrl + new.select('a')[0].get('href').strip()
                cur.execute('select count(1) from news_daily where url=%s',(url))
                if cur.fetchone()[0] == 0 :
                    

                    try:
                        contentRes = requests.get(url, timeout=5)
                        contentRes.encoding = 'utf-8'
                        if contentRes.status_code == 200:
                            contentSoup = BeautifulSoup(contentRes.text, 'html.parser')

                            publishdate = contentSoup.select('.smallList > li')[0].text.replace("日期", "").strip()
                            publishdate = datetime.strptime(publishdate, '%d.%m.%Y').strftime('%Y%m%d')
                            #if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                            #    continue
                            if int(publishdate) > int(deleteFromDate) :
                                
                                bodyContent = contentSoup.select('#bodyContent')[0]
                                contents = bodyContent.select('p')
                                content = cc.convert(''.join([c.text.strip() for c in contents]))
                                cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s,%s,%s,%s,%s,%s)',(web, title, content, publishdate, url, creationdate))
                                cur.execute('commit')
                                c = c + 1

                    except requests.exceptions.RequestException as e:
                        print('Exception DWNewsCrawling:'+str(e)) 
    print('DW ',creationdate,' total:',c)
    cur.close()
    conn.close()

if __name__ == "__main__":
    WebCrawling()    