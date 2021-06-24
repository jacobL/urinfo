from bs4 import BeautifulSoup
import requests
import pymysql
from datetime import datetime, timedelta,timezone
from google_trans_new import google_translator
import time
import random
import dbconfig

def gl_translator(text, lang_src, lang_tgt) :
    url_suffix_list = ['ac','ad','ae','al','am','as','at','az','ba','be','bf','bg','bi','bj','bs','bt','by','ca','cat','cc','cd','cf','cg','ch','ci','cl','cm','cn','co.ao','co.bw','co.ck','co.cr','co.id','co.il','co.in','co.jp','co.ke','co.kr','co.ls','co.ma','co.mz','co.nz','co.th','co.tz','co.ug','co.uk','co.uz','co.ve','co.vi','co.za','co.zm','co.zw','co','com.af','com.ag','com.ai','com.ar','com.au','com.bd','com.bh','com.bn','com.bo','com.br','com.bz','com.co','com.cu','com.cy','com.do','com.ec','com.eg','com.et','com.fj','com.gh','com.gi','com.gt','com.hk','com.jm','com.kh','com.kw','com.lb','com.lc','com.ly','com.mm','com.mt','com.mx','com.my','com.na','com.ng','com.ni','com.np','com.om','com.pa','com.pe','com.pg','com.ph','com.pk','com.pr','com.py','com.qa','com.sa','com.sb','com.sg','com.sl','com.sv','com.tj','com.tr','com.tw','com.ua','com.uy','com.vc','com.vn','com','cv','cx','cz','de','dj','dk','dm','dz','ee','es','eu','fi','fm','fr','ga','ge','gf','gg','gl','gm','gp','gr','gy','hn','hr','ht','hu','ie','im','io','iq','is','it','je','jo','kg','ki','kz','la','li','lk','lt','lu','lv','md','me','mg','mk','ml','mn','ms','mu','mv','mw','ne','nf','nl','no','nr','nu','pl','pn','ps','pt','ro','rs','ru','rw','sc','se','sh','si','sk','sm','sn','so','sr','st','td','tg','tk','tl','tm','tn','to','tt','us','vg','vu','ws']
    isSuccess = False
    url_suffix_inx = random.randint(0, len(url_suffix_list)-1)
    content_tw = ''
    while isSuccess == False :
        try :
            translator = google_translator(url_suffix=url_suffix_list[url_suffix_inx])        
            content_tw = translator.translate(text, lang_src=lang_src, lang_tgt=lang_tgt)
            isSuccess = True
        except Exception as e:
            url_suffix_inx = random.randint(0, len(url_suffix_list)-1)
    return content_tw   

def WebCrawling(days=5):
    host = '10.55.23.101'
    port = 33060
    user = 'root'
    passwd = "1234"
    db = 'idap'
    
    showPrintMSG = 1 # 0:不呈現，1:呈現 debug mode
    archiveDate = 10
    web = 'un'
    language = 'en'
    sleep_sec = 2
    lang_src=language
    lang_tgt='zh-tw'
    tag = 'international'
    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    creationdate = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')
    
    baseUrl = "https://news.un.org/"
    targetUrl = "https://news.un.org/en/news/{}{}?page={}"
    targetArr = {
        "region": [
            "africa", "americas", "asia-pacific", "middle-east", "europe"
            ],
        "topic": [
            "peace-and-security", "climate-change", "women", "culture-and-education", "economic-development", "human-rights",
            "law-and-crime-prevention", "sdgs", "humanitarian-aid", "un-affairs", "health", "migrants-and-refugees"
            ],
        "interviews": [""],
        "features": [""],
        "gallery": [""],
        "audio-product": [
            "news-brief", "podcast-the-lid-is-on", "focus-gender", "un-and-africa", ""
        ],
        "un-podcasts": [""],
    }
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
    cur = conn.cursor()
    
    c = 0
    for key, values in targetArr.items():
        for v in values:
            flag = True
            for page in range(0, 2):
                if flag is False:
                    break

                res = requests.get(targetUrl.format(key, "/" + v, page), headers=header)
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    news = soup.select('#block-system-main > .view > .view-content > .views-row')
                    for new in news:
                        publishdate = new.select('.date-display-single')[0].get('content')[0:10].replace('-', '')
                        #if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                        if int(publishdate) > int(deleteFromDate) : 
                            title = new.select('.body-wrapper > .story-title')[0].text
                            url = baseUrl + new.select('.body-wrapper > .story-title > a')[0].get('href').strip()
                            cur.execute('select count(1) from news_daily_source where url=%s',(url))
                            if cur.fetchone()[0] == 0 : 
                                try :
                                    contentRes = requests.get(url, timeout=5)
                                    contentRes.encoding = 'utf-8'
                                    if contentRes.status_code == 200 :
                                        contentSoup = BeautifulSoup(contentRes.text, 'html.parser')
                                        summary = contentSoup.select('.field-name-field-news-story-lead')[0].text
                                        contents = contentSoup.select('.field-name-field-text-column > .field-items > .field-item > p')
                                        content = ''.join([c.text.strip() for c in contents])
                                        content = summary + " " + content
                                        content_tw = gl_translator(content, lang_src, lang_tgt)
                                        title_tw = gl_translator(title, lang_src, lang_tgt)
                                        cur.execute('insert into news_daily_source(web, title, title_tw, content, content_tw, publishdate, url, creationdate,language,tag)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(web, title, title_tw, content, content_tw, publishdate, url, creationdate,language,tag))
                                        cur.execute('commit')
                                        c = c + 1
                                except requests.exceptions.RequestException as e:
                                    print('Exception UNNewsCrawling:'+str(e))
    print('UN ',creationdate,' total:',c)
    cur.close()
    conn.close()
    
if __name__ == "__main__":
    WebCrawling()
