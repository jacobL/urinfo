from bs4 import BeautifulSoup
import requests
import pymysql
from datetime import datetime, timedelta,timezone
from google_trans_new import google_translator
import time
import random
import dbconfig

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    
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
    web = 'cnn'
    language = 'en'
    sleep_sec = 2
    lang_src=language
    lang_tgt='zh-tw'

    conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
    cur = conn.cursor()

    baseUrl = 'https://edition.cnn.com'
    InitUrl = 'https://edition.cnn.com/business'
    res = requests.get(InitUrl)
    soup = BeautifulSoup(res.text, 'html.parser')
    newsList = soup.select("div.zn__containers li")
    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    creationdate = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')  # 轉換時區 -> 東八區

    c = 0
    for i in range(0,len(newsList)):
        try:
            title = soup.select("div.zn__containers li a")[i].text
            if title == '' :
                title = soup.select("h1.pg-headline")[0].text
            #print('title:',title)    
            url = baseUrl+soup.select("div.zn__containers li a")[i].get('href')
            cur.execute('select count(1) from news_daily_source where url=%s',(url))
            if cur.fetchone()[0] == 0 :
                if RepresentsInt(url.split('/')[3]) :
                    publishdate = url.split('/')[3]+url.split('/')[4]+url.split('/')[5]
                    if int(publishdate) > int(deleteFromDate) :
                        resContent = requests.get(url)
                        soupContent = BeautifulSoup(resContent.text, 'html.parser')
                        divList = soupContent.select("div.zn-body__paragraph")
                        if len(divList) > 0 :
                            divList = soupContent.select("div.zn-body__paragraph")

                            tag = url.split('/')[6]
                            content = ''.join([c.text.strip() for c in divList])
                            content_tw = gl_translator(content, lang_src, lang_tgt)
                            title_tw = gl_translator(title, lang_src, lang_tgt)
 
                            #print(i,'\n title:', title, '\n publishdate:',publishdate, '\n tag:',tag,'\n url:', url)
                            cur.execute('insert into news_daily_source(web, title, title_tw, content, content_tw, publishdate, url, creationdate,language,tag)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(web, title, title_tw, content, content_tw, publishdate, url, creationdate,language,tag))
                            cur.execute('commit')
                            c = c + 1
        except Exception as e:
            print('Exception CNNCrawling:'+str(e)) 
    print('CNN ',creationdate,' total:',c)
    cur.close()
    conn.close()
    

if __name__ == "__main__": 
    WebCrawling()    