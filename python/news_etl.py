import pymysql
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date, datetime, timedelta
 
import opencc
import time  
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="G2G")

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances

# db config
host = '10.55.23.168' 
port=33060
user = 'root'
passwd = "1234"
db = 'idap'

showPrintMSG = 0 # 0:不呈現，1:呈現 debug mode

# Step1. Disaster Keyword
#單句斷詞保留數字
def jiebacut_word_num(Q_Word,jieba):
    
    conn = pymysql.connect( host = host , port=port , user = user , passwd = passwd , db = db )          
    cur = conn.cursor() 

    cur.execute('SELECT stopword FROM stopword')
    results = cur.fetchall()
    stop_words=[]
    for db_row in results:
        stop_words.append(db_row[0])

    Word_list = ''
    c=1
    for w in jieba.cut(Q_Word, cut_all=False):
        if w.lower().strip() not in stop_words and w.lower().strip() != '': # 避開停用字與空白
            tongyici_w=w.lower().strip()
            #print(w.lower().strip())
            if c == 1 :
                Word_list=tongyici_w
            else :    
                Word_list=Word_list+' '+ tongyici_w
            c = c + 1                  
    cur.close()
    conn.close()
    return Word_list     # 空白區隔的字串

def news_disaster_keyword():
    if showPrintMSG :
        print('start news_disaster_keyword ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor () 
    cur1 = conn . cursor ()  
    nametype = 'DSTR1'
    
    conn = pymysql.connect( host = host , port=port , user = user , passwd = passwd , db = db )          
    cur = conn.cursor() 
    cur1 = conn.cursor() 

    cc = opencc.OpenCC('s2t')

    # 0.加入jieba關鍵字
    cur.execute('SELECT jiebaword FROM jiebadict where status=0') 
    for r in cur:
        jieba.add_word(r[0])

    # 1.產生content的斷詞結果，以詞空格區隔。 
    cur.execute('SELECT id, content FROM news_daily where jiebalist is null') 
    num = 1
    for r in cur:
        id=r[0]
        cut_word_re = jiebacut_word_num(cc.convert(r[1]),jieba) 
        cur1.execute('update news_daily set jiebalist=%s where id=%s',(cut_word_re,id))
        cur1.execute('commit')
        #if num%100 == 0 :
        #    print(num)
        num = num + 1
        #print(cut_word_re)

    # 2.document是全部的文章list    
    document = [] 
    cur.execute('SELECT jiebalist FROM news_daily where jiebalist is not null and status=0 order by id')
    for r in cur:
        #print(r[0])
        document.append(r[0])

    article_id = []
    titles = []
    publishdate_list = []
    cur.execute('SELECT id,title,publishdate FROM news_daily where jiebalist is not null and status=0 order by id') 
    for r in cur:
        article_id.append(r[0]) 
        titles.append(r[1])  
        publishdate_list.append(r[2])  

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(document)  

    #query_list = ['流感', '新冠,肺炎', '戰爭', '爆炸', '停電', '地震', '停工,罷工', '霾', '森林大火', '風災', '大雪', '海嘯', '洪水', '暴雨', '停水', '火山爆發', '冰雹']
    query_list = {'burning':'野火,火災,大火,失火,起火,火警','flood':'洪水,水災,水患','volcano':'火山','earthquake':'地震','virus':'流感,感冒','tsunami':'海嘯',
    'typhoon':'風災,龍捲風,颱風','snow':'大雪,暴風雪,雪災,豪雪','rainy':'暴雨','mist':'霾','sandstorm':'沙暴','explosion':'爆炸','covid-19':'新冠,新冠肺炎,武漢肺炎,武肺,冠狀,covid-19',
    'strick':'停工,罷工','wateroutage':'停水,斷水','poweroutage':'停電','war':'戰爭','hail':'冰雹,雹災'}
    for query in query_list:
        #output_id = getQuerySimiliarArticle(query, vectorizer, X, article_id, titles)
        ######### query字詞處理 #########
        query_corpus = [','.join(jieba.cut(query_list[query]))]    
        query_vec = vectorizer.transform(query_corpus)


        #====================================================================== 
        ######### 計算相似度並產出結果 #########
        cs = cosine_distances(query_vec, X).flatten()
        output_id = []
        #print('='*30, '\n', query_list[query])
        for idx in cs.argsort():
            if cs[idx] < 0.9:
            #if cs[idx] < 1:    
                #print('id:', article_id[idx], '\n', titles[idx], '\n相似度為: ',cs[idx],' query:',query)
                #print('id:', article_id[idx], ' query:',query)
                output_id.append(article_id[idx])
                #cur.execute('update news_daily set tag=concat(tag, %s) where id=%s and tag is not null',(','+query,article_id[idx]))
                #cur.execute('update news_daily set tag=%s where id=%s and tag is null',(query,article_id[idx]))
                cur.execute('insert ignore into news_ner(newsid,entity,nametype,publishdate)values(%s,%s,"DSTR1",%s)',(article_id[idx],query_list[query].split(',')[0],publishdate_list[idx]))
                cur.execute('commit')    
    cur.close()
    cur1.close()
    conn.close()
    
# Step 2.Country-City-Disaster
def find_CountryCity_for_disaster(): 
    if showPrintMSG :
        print('start find_CountryCity_for_disaster ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor () 
    cur1 = conn . cursor () 
    
    # 取得所有AML城市清單
    cur.execute("SELECT city FROM aml_country_city order by SYSTEM_FACTORY_count desc")
    cityList = [item[0] for item in cur.fetchall()]
    
    # 建立AML城市查詢國家的dict
    cur.execute("SELECT city,country FROM aml_country_city order by SYSTEM_FACTORY_count desc")
    cityCountryList = {item[0]:item[1] for item in cur.fetchall()}
    
    # 從上次的進度開始，取未處理的
    cur.execute("SELECT max(newsid) FROM news_disaster")
    fromNewsid = cur.fetchone()[0]
    if showPrintMSG :
        print('fromNewsid:',fromNewsid)
    if fromNewsid is None :
        fromNewsid = 0
        
    cur.execute("SELECT newsid,entity,content,b.publishdate FROM news_ner a left join news_daily b on a.newsid = b.id WHERE nametype='DSTR1' and newsid>(SELECT IFNULL(max(newsid), 0)-1000 FROM news_disaster)")
    for r in cur :
        newsid = r[0]
        entity = r[1]
        content = r[2]
        publishdate = r[3]
        
        for city in cityList :
            if city in content :
                country = cityCountryList[city]
                
                cur1.execute("select count(1) from news_disaster where newsid = %s and country = %s and city = %s and eventtype = %s",(newsid,country,city,entity)) 
                if str(cur1.fetchone()[0]) == '0' :
                    if showPrintMSG :
                        print('entity:',entity,' , city:',city,' , country:',country)
                    cur1.execute("insert ignore into news_disaster(newsid,country,city,eventtype,publishdate)values(%s,%s,%s,%s,%s)",(newsid,country,city,entity,publishdate))
 
    cur1.execute("commit")                

# Step 3.Country-City-AML-Disaster
def find_CountryCityAML_for_disaster(): 
    if showPrintMSG :
        print('start find_CountryCityAML_for_disaster ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor () 
    cur1 = conn . cursor () 
    
    # 取得所有AML城市清單
    cur.execute("SELECT city FROM aml_country_city order by SYSTEM_FACTORY_count desc")
    cityList = [item[0] for item in cur.fetchall()]
    
    # 建立AML城市查詢國家的dict
    cur.execute("SELECT city,country FROM aml_country_city order by SYSTEM_FACTORY_count desc")
    cityCountryList = {item[0]:item[1] for item in cur.fetchall()}
    
    # 從上次的進度開始，取未處理的
    cur.execute("SELECT max(newsid) FROM news_disaster")
    fromNewsid = cur.fetchone()[0]
    if showPrintMSG :
        print('fromNewsid:',fromNewsid)
    if fromNewsid is None :
        fromNewsid = 0
        
    cur.execute("SELECT newsid,entity,content,b.publishdate FROM news_ner a left join news_daily b on a.newsid = b.id WHERE nametype='DSTR1' and newsid>(SELECT IFNULL(max(newsid), 0)-1000 FROM news_disaster)")
    for r in cur :
        newsid = r[0]
        entity = r[1]
        content = r[2]
        publishdate = r[3]
        
        for city in cityList :
            if city in content :
                country = cityCountryList[city]
                
                cur1.execute("select count(1) from news_disaster where newsid = %s and country = %s and city = %s and eventtype = %s",(newsid,country,city,entity)) 
                if str(cur1.fetchone()[0]) == '0' :
                    if showPrintMSG :
                        print('entity:',entity,' , city:',city,' , country:',country)
                    cur1.execute("insert ignore into news_disaster(newsid,country,city,eventtype,publishdate)values(%s,%s,%s,%s,%s)",(newsid,country,city,entity,publishdate))
 
    cur1.execute("commit")   
    
# Step 4. Varify Country
def varify_country():
    #print('start varify_country ',datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor () 

    cur.execute("update news_disaster set country='朝鮮' where country='朝鮮民主主義人民共和國'") 
    cur.execute("update news_disaster set country='比利時' where country='比利時-比利時-比利時'") 
    cur.execute("update news_disaster set country='比利時' where country='比利時/比利時/比利時'") 
    cur.execute("update news_disaster set country='厄立特里亞厄立特里亞' where country='厄立特里亞厄立特里亞.رتريا'")
    cur.execute("update news_disaster set country='吉布提' where country='吉布提;吉布提'")
    cur.execute("update news_disaster set country='韓國' where country='大韓民國'")
    cur.execute("update news_disaster set country='土耳其' where country='火雞'")
    cur.execute("update news_disaster set country='敘利亞' where country='蘇裏亞敘利亞'")
    cur.execute("update news_disaster set country='瑞士' where country='施維茲/瑞士/瑞士/斯維茲拉'")
    cur.execute("update news_disaster set country='捷克' where country='捷克語'")
    cur.execute("update news_disaster set country='沙特阿拉伯' where country='沙特阿拉伯/沙特阿拉伯'")
    cur.execute("update news_disaster set country='荷蘭' where country='荷蘭人'")
    cur.execute("update news_disaster set country='ایران' where country='伊朗'")
    cur.execute("update news_disaster set country='新西蘭' where country='新西蘭/奧特羅阿'")
    
    # 20210118
    cur.execute("update news_disaster set country='美國' where country='美利堅合衆國/美利堅合眾國'")
    cur.execute("update news_disaster set country='韓國' where country='韓國/南韓'")
    cur.execute("update news_disaster set country='英國' where country='英國/英國'")
    cur.execute("update news_disaster set country='法國' where country='法國/法國'")
    cur.execute("update news_disaster set country='烏克蘭' where country='烏克蘭/烏克蘭'")
    cur.execute("update news_disaster set country='俄羅斯' where country='俄羅斯/俄羅斯'")    
    cur.execute("update news_disaster set country='帛琉' where country='帕勞 / 帛琉'")
    cur.execute("update news_disaster set country='巴布亞新畿內亞' where country='巴布亞新幾內亞 / 巴布亞紐幾內亞 / 巴布亞新畿內亞'")
    cur.execute("update news_disaster set country='哈薩克' where country='哈薩克斯坦/哈薩克'")    
    cur.execute("update news_disaster set country='寮國' where country='老撾/寮國'")
    cur.execute("update news_disaster set country='菲律賓' where country='菲律賓 / 菲律賓'")
    cur.execute("update news_disaster set country='約旦' where country='約旦/約旦'")
    cur.execute("update news_disaster set country='敘利亞' where country='敘利亞/敘利亞'")
    cur.execute("update news_disaster set country='塞浦路斯' where country='賽普勒斯/塞浦路斯/塞浦路斯'")
    
    cur.execute("update news_disaster set country='美國' where country='美利堅合衆國'")
    
    cur.execute("update news_disaster set country = '台灣' where country = '臺灣'") 
    cur.execute("update news_disaster set city = REPLACE(city, '臺', '台') where country = '台灣' and city like '臺%'")
    
    cur.execute("commit")    

# Step 5. Delete Old Data
def delete_old_data():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor () 
    archiveDate = 10
    deleteFromDate = datetime.strftime(datetime.now() - timedelta(archiveDate), '%Y%m%d')
    cur.execute("delete from news_ner WHERE newsid in (SELECT id FROM news_daily WHERE publishdate<=%s)",(deleteFromDate))
    cur.execute("delete from news_disaster WHERE newsid in (SELECT id FROM news_daily WHERE publishdate<=%s)",(deleteFromDate))
    cur.execute("delete FROM news_daily WHERE publishdate<=%s",(deleteFromDate))
    cur.execute("commit")     
def news_etl():
    delete_old_data()
    news_disaster_keyword()
    find_CountryCity_for_disaster()
    varify_country()
    
news_etl()    