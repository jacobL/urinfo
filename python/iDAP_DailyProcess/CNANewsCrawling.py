from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pymysql

def WebCrawling():
    host = '10.55.23.101'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'
    web = "cna"  #中央社 
    try:
        targetUrl = "https://www.cna.com.tw/cna2018api/api/WNewsList"
        conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
        cur = conn.cursor()
        c=0
        for page in range(1, 5):
            formData = {'pageidx': page, 'pagesize': '20', 'action': '0', 'category': 'aall'}
            res = requests.post(targetUrl.format(page), data=formData)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                result_json = res.json()
                news = result_json['ResultData']['Items']                
                for new in news:   
                    c=c+1
                    tag = new["ClassName"]
                    url = new["PageUrl"]
                    title = new["HeadLine"]
                    publishdate = new["CreateTime"][0:10].replace('/','')
                    creationdate = datetime.now()
                    content = ''
                    contentRes = requests.get(url)
                    contentRes.encoding = 'utf-8'
                    if contentRes.status_code == 200:
                        #contentSoup = BeautifulSoup(contentRes.text, 'lxml')
                        contentSoup = BeautifulSoup(contentRes.text, 'html.parser')
                        
                        content = contentSoup.select('div.paragraph')[0].text
                        index = content.find('延伸閱讀')
                        if index > -1:
                            content = content[0: index]
                        cur.execute('insert ignore into news_daily(web, title, content, publishdate, url, creationdate)values(%s, %s, %s, %s, %s, %s)',(web, title, content, publishdate, url, creationdate))
                        cur.execute('commit')
        print('2.CNANews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception CNANewsCrawling:'+str(e))

if __name__ == "__main__":
    WebCrawling()
