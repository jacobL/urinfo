# WS斷詞、POS詞性標記、NER命名實體識別
from ckiptagger import WS, POS, NER
import pymysql

# db config
host = '10.55.52.98' 
port=33060
user = 'root'
passwd = "1234"
db = 'idap'
# 啟動模型
ws = WS("./data")
pos = POS("./data")
ner = NER("./data")

nametypeList = ['GPE','ORG','FAC','PERSON','LOC','NORP','PRODUCT','LAW','WORK_OF_ART','EVENT']
nametypeListALL = ['GPE','ORG','FAC','PERSON','LOC','NORP','PRODUCT','LAW','WORK_OF_ART','EVENT', 'PERCENT','DATE','CARDINAL','MONEY','ORDINAL','QUANTITY','TIME','LANGUAGE']
conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
cur = conn . cursor () 
cur1 = conn . cursor () 
cur.execute("delete from news_ner")
cur.execute("ALTER TABLE idap.news_ner AUTO_INCREMENT = 1")

#cur.execute("select id,content from news_daily where web not in ('nhk') order by id desc limit 0,30 ")
# 'nikkei','hket','worldjournal','epochtimes','plataformamedia','kyodonews','rfi','storm','crossing','thenewslens',
#'newtalk','worldjournal','',''
#cur.execute("select id,content,web,publishdate from news_daily where web not in ('nhk') and ner_status=0 and id>141949 order by id limit 1000")
cur.execute("select id,content,web,publishdate from news_daily where web in ('nikkei','hket','worldjournal','epochtimes','plataformamedia','kyodonews','rfi','storm','crossing','thenewslens','newtalk','worldjournal') and ner_status=0 order by id desc limit 1000")
#cur.execute("select id,content from news_daily where id=148882")

c=0
for r in cur :
    c=c+1
    if c%80 == 0:
        #cur.close()
        cur1.close()
        conn.close()        
        conn = pymysql.connect ( host = host , port = port , user = user , passwd = passwd , db = db)         
        cur1 = conn . cursor () 
    entityName = {}    
    newsid = r[0]
    content = r[1]
    web = r[2]
    publishdate = r[3]
    
    #print(content)
    
    ws_results = ws([content],segment_delimiter_set={'?', '？', '!', '！', '。', ',','，', ';', ':', '、','）','（','/'})
    pos_results = pos(ws_results)
    ner_results = ner(ws_results, pos_results)
    
    # 彙整有用的 nametype
    for name in ner_results[0]:
        nametype = name[2]
        entity = name[3].strip() 
        if nametype in nametypeList :
            key = entity+'||'+nametype
            if key in entityName :
                entityName[key] = entityName[key] + 1
            else :    
                entityName[key] = 1 
                
    print(c,'.',newsid,' len(entityName)=',len(entityName))
    # insert ner table
    if len(entityName) > 0:
        for EN in entityName :
            entity = EN.split('||')[0]
            nametype = EN.split('||')[1]
            count = entityName[EN]
            cur1.execute("insert ignore into  idap.news_ner(newsid,entity,nametype,count,web,publishdate)values(%s,%s,%s,%s,%s,%s)",(newsid,entity,nametype,count,web,publishdate))
    cur1.execute("update news_daily set ner_status=1 where id=%s",(newsid))            
    #print(entityName)
    #print('\n\n')
    cur1.execute("commit")