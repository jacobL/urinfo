import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from bs4 import BeautifulSoup
import requests
from google_trans_new import google_translator
import pymysql
from datetime import datetime, timedelta,timezone
from google_trans_new import google_translator
import time
import random
import dbconfig

## mapp #######
import urllib
import requests
import json

#host = '10.55.23.101'
#port = 33060
#host = '10.55.14.206'
#port = 33065
#user = 'root'
#passwd = "1234"
#db = 'idap'
lang_tgt='zh-tw'

useraccount = 'api_smartpush' 
apikey = '9AE29D27-02F2-016A-11AF-01C9907ABB28'
chatsn = '147965'



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

def google_request(q) :
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    url='https://www.google.com/search?q='+q+'&tbm=nws&tbs=qdr:d'
    res = requests.get(url, headers=header)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    news = soup.select('.dbsr')
    
    conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
    cur = conn.cursor()
    
    result = {}
    
    if len(news) > 0 :
                
        #print(q,'有',len(news),'筆資料\n\n')
        translator = google_translator(url_suffix="ac")        
        c=0
        for new in news :            
            try :
                url = new.select('a')[0].get('href')
                if new.find_all('div')[1].text == '' : # 有照片
                    web = new.find_all('div')[6].text
                    title = new.find_all('div')[7].text
                    abstract = new.find_all('div')[9].text
                    publishdate = new.find_all('div')[10].text
                else :                                 # 沒照片
                    web = new.find_all('div')[1].text
                    title = new.find_all('div')[2].text
                    abstract = new.find_all('div')[4].text
                    publishdate = new.find_all('div')[5].text

                lang_src = translator.detect(title)

                if lang_src != 'zh-tw' and lang_src != 'zh-CN' :
                    title_tw = gl_translator(title, lang_src, lang_tgt)
                    abstract_tw = gl_translator(abstract, lang_src, lang_tgt)             
                    #print('web:',web,'\ntitle:',title,' title_tw:',title_tw,'\nabstract:',abstract,' abstract_tw:',abstract_tw,'\npublishdate:',publishdate,'\nurl:',url,'\n\n')
                #else :
                    #print('web:',web,'\ntitle:',title,'\nabstract:',abstract,'\npublishdate:',publishdate,'\nurl:',url,'\n\n')
                tmp = {}    
                tmp['web'] = web
                tmp['title'] = title
                tmp['title_tw'] = title_tw
                tmp['abstract'] = abstract
                tmp['abstract_tw'] = abstract_tw            
                tmp['url'] = url
                tmp['language'] = lang_src
                result[c] = tmp
                c=c+1
            except Exception as e:
                pass
    else :
        print(q,' google 沒資料!')
        
    cur.close()
    conn.close()            
    return result
 
def mappChatsn(chatsn,content) :
    
    result = mapppost_content(useraccount,apikey,chatsn,content)
    return result
    
def mapppost_content(useraccount,apikey,chatsn,content):
    content_utf8 = content.encode("UTF-8")#轉UTF8
    content_utf8_url = urllib.parse.quote_plus(content_utf8)#轉URL
    url = "http://mapp.local/teamplus_innolux/API/IMService.ashx"
    payload = "ask=sendChatMessage&account={}&api_Key={}&chat_sn={}&content_type=1&msg_content={}&file_show_name=&undefined=".format(useraccount,apikey,chatsn,content_utf8_url)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded"
        }
    response = requests.request("POST", url, data=payload, headers=headers)     
    result = json.loads(response.text)
                
    if not result['IsSuccess'] :
        return [3,result['ErrorCode'],result['IsSuccess'],result['Description']]
    
    return [0,result['ErrorCode'],result['IsSuccess'],result['Description']]   

def main():
    conn = pymysql.connect(host=dbconfig.host, port=dbconfig.port, user=dbconfig.user, passwd=dbconfig.passwd, db=dbconfig.db)
    cur = conn.cursor()
    cur1 = conn.cursor()

    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    creationdate = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')    
    
    #cur.execute("SELECT id,keyword,keyword_tw FROM news_keyword_subscribe WHERE status=0 and id in (147,148,149)")
    cur.execute("SELECT id,keyword,keyword_tw FROM news_keyword_subscribe WHERE status=0 and id in (147,148,149)")
    for r in cur :
        newsContent = ''
        subscribeid = r[0]
        q = r[1] 
        google_result = google_request(q)
        count = 0
        print(q)
        for i in google_result :        
            url = google_result[i]['url']
            #print(google_result[i])
            cur1.execute("select count(1) from google_news where url=%s",(url))
            if cur1.fetchone()[0] == 0 :
                count = count + 1
                web = google_result[i]['web']
                language = google_result[i]['language']
                title = google_result[i]['title']
                abstract = google_result[i]['abstract']
                if language != 'zh-CN' :        
                    title_tw = google_result[i]['title_tw']
                    abstract_tw = google_result[i]['abstract_tw']
                    newsContent = newsContent+'\n'+str(count)+' .'+title_tw+'('+title+')，'+abstract_tw+'('+abstract+')\n'+url
                else :     
                    title_tw = None
                    #abstract_tw = None
                    newsContent = newsContent+'\n'+str(count)+' .'+title+'，'+abstract+'\n'+url        

                cur1.execute("insert into google_news(subscribeid,web,title,title_tw,url,creationdate)values(%s,%s,%s,%s,%s,%s)",(subscribeid,web,title,title_tw,url,creationdate))
                cur1.execute("commit")
                #print(google_result[i])

        newsContent = '關鍵字: '+q+' 有'+str(count)+'筆新聞。\n'+newsContent
        if count > 0 :
            result = mappChatsn(chatsn,newsContent) 
        
        #print('關鍵字: '+q+' 有'+str(count)+'筆新增的新聞。\n')    
        #print('====================================\n',newsContent)
    cur.close()
    cur1.close()
    conn.close()        

main()