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

def WebCrawling():

    showPrintMSG = 1 # 0:不呈現，1:呈現 debug mode
    archiveDate = 10
    web = 'dw'
    language = 'en'
    sleep_sec = 2
    lang_src=language
    lang_tgt='zh-tw'
    
    baseUrl = "https://www.dw.com"
    targetUrl = "https://www.dw.com/en/top-stories/{}" 
    targetArr = ["s-9097", "germany/s-1432", "coronavirus/s-32798", "world/s-1429", "business/s-1431", "science/s-12526","environment/s-11798"]
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
    cur = conn.cursor()
     
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

                title = new.select('a > h2')[0].text
                url = baseUrl + new.select('a')[0].get('href').strip()
                
                cur.execute('select count(1) from news_daily_source where url=%s',(url))
                if cur.fetchone()[0] == 0 :
                    try:
                        
                        contentRes = requests.get(url, timeout=5)
                        contentRes.encoding = 'utf-8'
                        if contentRes.status_code == 200:
                            contentSoup = BeautifulSoup(contentRes.text, 'html.parser')
                            
                            publishdate = contentSoup.select('.smallList > li')[0].text.replace("Date", "").strip()
                            #print(publishdate,url)
                            if publishdate == 'Send us an e-mail.' :
                                continue
                            publishdate = datetime.strptime(publishdate, '%d.%m.%Y').strftime('%Y%m%d') 
                            #if publishdate < (datetime.today() - timedelta(days=1)).strftime('%Y%m%d'):
                            #    continue
                            if int(publishdate) > int(deleteFromDate) : 
                                
                                bodyContent = contentSoup.select('#bodyContent')[0]
                                contents = bodyContent.select('p')
                                content = ''.join([c.text.strip() for c in contents])
                                content_tw = gl_translator(content, lang_src, lang_tgt)
                                title_tw = gl_translator(title, lang_src, lang_tgt)
                                cur.execute('insert into news_daily_source(web, title, title_tw, content, content_tw, publishdate, url, creationdate,language,tag)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(web, title, title_tw, content, content_tw, publishdate, url, creationdate,language,tag))
                                cur.execute('commit')
                                c = c + 1

                    except requests.exceptions.RequestException as e:
                        print('Exception DWNewsCrawling:'+str(e)) 
    print('DW ',creationdate,' total:',c)
    cur.close()
    conn.close()

if __name__ == "__main__":
    WebCrawling()    