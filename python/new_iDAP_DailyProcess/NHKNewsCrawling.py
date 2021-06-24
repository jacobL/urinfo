from bs4 import BeautifulSoup
import requests
import pymysql
from datetime import datetime, timedelta
from google_trans_new import google_translator
import time
import random
import dbconfig

def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)
        
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
    
    showPrintMSG = 1 # 0:不呈現，1:呈現 debug mode
    archiveDate = 10
    web = 'nhk'
    language = 'jp'
    sleep_sec = 2
    lang_src=language
    lang_tgt='zh-tw'
    tag = ''

    targetUrl = "https://www3.nhk.or.jp/news/json16/new_{}.json"
    baseUrl = "https://www3.nhk.or.jp/news/"
    
    
    conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
    cur = conn.cursor()
    c=0
    creationdate = datetime.now()
    for page in range(1, 11): # 超過10就404
        try:
            res = requests.get(targetUrl.format(str(page).zfill(3)))
            #print(targetUrl.format(str(page).zfill(3)))
            res.encoding = 'utf-8'
            creationdate = datetime.now()
            if res.status_code == 200:
                result_json = res.json()

                for item in result_json['channel']['item']:
                    title = item['title']
                    originUrl = item['link']
                    url = baseUrl + originUrl
                    cur.execute('select count(1) from news_daily_source where url=%s',(url))
                    if cur.fetchone()[0] == 0 :
                        contentRes = requests.get(url)
                        contentRes.encoding = 'utf-8'
                        if contentRes.status_code == 200: 
                            soup = BeautifulSoup(contentRes.text, 'html.parser')
                            publishdate = (soup.select('time')[0].get('datetime'))[0:10].replace('-', '')
                            if publishdate < (datetime.today() - timedelta(days=days)).strftime('%Y%m%d'):
                                return
                            c=c+1
                            content = soup.select('div.content--detail-body')[0].text 
                            title_tw = gl_translator(title, lang_src, lang_tgt)
                            content_tw = gl_translator(content, lang_src, lang_tgt)
                            #print(publishdate)
                            #print(page,url)
                            #print(title_tw,' ',title)
                            #print(content)
                            #print(content_tw+'\n')

                            cur.execute('insert into news_daily_source(web,title,title_tw,content,content_tw,publishdate,url,creationdate,language)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',(web,title,title_tw,content,content_tw, publishdate,url,creationdate,language))
                            cur.execute('commit')
            else :
                print('res.status_code:',res.status_code)
        except Exception as e:
            print('Exception NHKNewsCrawling:'+str(e)) 
    print('NHKNews ',creationdate,' total:',c)
    cur.close()
    conn.close()    
    
if __name__ == "__main__":
    WebCrawling()    