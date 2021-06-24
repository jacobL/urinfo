import pymysql
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import dbconfig
def WebCrawling(days=5):
    web = "appledaily" 
    
    try:
        conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)

        cur = conn.cursor()
        baseUrl = 'https://tw.appledaily.com'
        targetUrl = 'https://tw.appledaily.com/pf/api/v3/content/fetch/query-feed'
        param = {
            'query': '{"feedOffset":0,"feedQuery":"type%3Astory%20AND%20taxonomy.primary_section._id%3A%2F%5C%2Frealtime.*%2F","feedSize":"100","sort":"display_date:desc"}',
            'filter': '{_id,content_elements{_id,canonical_url,created_date,display_date,headlines{basic},last_updated_date,promo_items{basic{_id,caption,created_date,height,last_updated_date,promo_image{url},type,url,version,width},canonical_website,credits,display_date,first_publish_date,location,publish_date,related_content,subtype},revision,source{additional_properties,name,source_id,source_type,system},taxonomy{primary_section{_id,path},tags{text}},type,version,website,website_url},count,type,version}'
        }
        res = requests.get(targetUrl, params=param)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            result_json = res.json()
            news = result_json['content_elements']
            c=0
            for new in news:
                c=c+1
                title = new['headlines']['basic']
                url = baseUrl + new['canonical_url']
                publishdate = new['display_date'][0:10].replace('-', '')
                if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                    return
                creationdate = datetime.now()
                content = ''
                contentres = requests.get(url)
                contentres.encoding = 'utf-8'
                if contentres.status_code == 200:
                    #contentsoup = BeautifulSoup(contentres.text, 'lxml')
                    contentsoup = BeautifulSoup(contentres.text, 'html.parser')                    
                    content = contentsoup.select('div#articleBody')[0].text
                    cur.execute('insert into news_daily(web, title, content, publishdate, url, creationdate) SELECT * FROM (SELECT %s, %s, %s, %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT url FROM news_daily WHERE url = %s) LIMIT 1',(web, title, content, publishdate, url, creationdate, url))
                cur.execute('commit')
        print('1.AppleNews ',creationdate,' total:',c)
        cur.close()
        conn.close()
    except Exception as e:
        print('Exception AppleNewsCrawling:'+str(e))
        
if __name__ == "__main__":
    WebCrawling()