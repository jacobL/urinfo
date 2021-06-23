#!/usr/bin/env python
# coding: utf-8
import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS, cross_origin
from collections import OrderedDict
import pymysql
import time
import json
import cx_Oracle 
from geopy.geocoders import Nominatim

 
from datetime import datetime, date,   timezone,timedelta
import urllib 
import requests
import os
import base64
#from requests_testadapter import Resp 
from shutil import copyfile
from io import BytesIO

from google_trans_new import google_translator
import random

import warnings
warnings.filterwarnings('ignore')

import re
import os
os.chdir("/usr/src")
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

# db config
#host = 'PC89600059495S' 
port=33060
host = '10.55.23.168' 


user = 'root'
passwd = "1234"
db = 'idap'

useraccount = 'api_smartpush' 
apikey = '9AE29D27-02F2-016A-11AF-01C9907ABB28'
chatsn_dev = '138897,138645' # 測試 後段:119046 , 前段:144915
chatsn_pro = '119046,144915' # 正式 後段:119046 , 前段:144915

# 0517 季禪 先關閉mapp
#chatsn_dev = 'abc,abc' # 測試 後段:119046 , 前段:144915
#chatsn_pro = 'abc,abc' # 正式 後段:119046 , 前段:144915


#守門員 突發事件通知  119046
#ID mapp測試群 88304  

# Oracle 
# 2021/1 舊的Oracle11 
connstr_dev = "SQE_AP/TSQEAP2020@10.56.172.113:1521/TJNCOMB"
schema_dev = "SCMP_ADM"

# 2021/1 新的Oracle19c

connstr_pro = "SQE_AP/PSQEAP2020@10.56.172.83:1521/PPMCDB"
schema_pro = "SCMP_ADM"

#PPMC_ADM.MAP_DISASTER_H
#SCMP_ADM.MAP_DISASTER_H
#PPMC_ADM.MAP_DISASTER_AREA
#SCMP_ADM.MAP_DISASTER_AREA

@app.route("/getEarthquake_tw", methods=['GET'])
def getEarthquake_tw():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    earthquake_list = OrderedDict();
    cur.execute("SELECT id,`index`,DATE_FORMAT(datetime,'%Y-%m-%d %H:%i:%S'),region,depth,mag,DATE_FORMAT(creationdate,'%Y-%m-%d %H:%i:%S') FROM earthquake_tw ORDER BY datetime DESC")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['index'] = r[1]
        tmp['datetime'] = r[2]
        tmp['region'] = r[3]
        tmp['depth'] = r[4]
        tmp['mag'] = r[5]
        tmp['creationdate'] = r[6]
        earthquake_list[c] = tmp
        c=c+1
        
    cur.close()
    conn.close()
    
    returnData = OrderedDict(); 
    returnData['earthquake_list'] = earthquake_list
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/getEarthquake", methods=['GET'])
def getEarthquake():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    earthquake_list = OrderedDict();
    cur.execute("SELECT id,datetime,latitude,longitude,depth,mag,region,status FROM earthquake ORDER BY datetime DESC")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['datetime'] = r[1]
        tmp['latitude'] = r[2]
        tmp['longitude'] = r[3]
        tmp['depth'] = r[4]
        tmp['mag'] = r[5]
        tmp['region'] = r[6]
        tmp['status'] = r[7]
        earthquake_list[c] = tmp
        c=c+1
        
    cur.close()
    conn.close()
    
    returnData = OrderedDict(); 
    returnData['earthquake_list'] = earthquake_list
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/getDailyData", methods=['GET'])
def getDailyData():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    # news_daily 第1層 每日新聞數量    
    news_daily = OrderedDict();
    cur.execute("SELECT publishdate,count(1) FROM news_daily GROUP by publishdate ORDER BY publishdate DESC")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['publishdate'] = r[0]
        tmp['count'] = r[1]
        news_daily[c] = tmp
        c=c+1
    
    # news_daily_detail 第1.1層 每日新聞數量    
    news_daily_detail = OrderedDict();
    cur.execute("SELECT publishdate,web,count(1) FROM news_daily GROUP by publishdate,web ORDER BY publishdate DESC,web")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['publishdate'] = r[0]
        tmp['web'] = r[1]
        tmp['count'] = r[2]
        news_daily_detail[c] = tmp
        c=c+1
        
    # news_ner 第二層 每日NER數量   
    news_ner = OrderedDict();
    cur.execute("SELECT publishdate,count(1) FROM news_ner GROUP by publishdate ORDER BY publishdate DESC")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['publishdate'] = r[0]
        tmp['count'] = r[1]
        news_ner[c] = tmp
        c=c+1
     
    # news_disaster 第三層 每日Disaster數量  
    news_disaster = OrderedDict();
    cur.execute("SELECT publishdate,count(1) from ( \
                select  a.newsid,b.publishdate from news_disaster a left join \
                (SELECT newsid,publishdate FROM news_ner) b on a.newsid=b.newsid) a GROUP \
                by publishdate ORDER by publishdate desc")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['publishdate'] = r[0]
        tmp['count'] = r[1]
        news_disaster[c] = tmp
        c=c+1
    
    # 日韓 每日各網的新聞數量
    news_source = OrderedDict();
    cur.execute("SELECT publishdate,web,count(1) FROM news_daily_source group by publishdate,web ORDER BY publishdate DESC")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['publishdate'] = r[0]
        tmp['web'] = r[1]
        tmp['count'] = r[2]
        news_source[c] = tmp
        c=c+1
        
    cur.close()
    conn.close()
    
    returnData = OrderedDict(); 
    returnData['news_daily'] = news_daily   
    returnData['news_daily_detail'] = news_daily_detail
    returnData['news_ner'] = news_ner
    returnData['news_disaster'] = news_disaster
    returnData['news_source'] = news_source
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response     

@app.route("/getDisasterMap", methods=['GET'])
def getDisasterMap():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    typhoonList = OrderedDict();
    cur.execute("SELECT name,name_ch,tc_id FROM typhoon ")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['name'] = r[0]
        tmp['name_ch'] = r[1]
        tmp['tc_id'] = r[2]
        typhoonList[c] = tmp
        c=c+1
        
    typhoonPathList = OrderedDict();
    cur.execute("SELECT id,tc_id,DATE_FORMAT(analysis_time,'%Y-%m-%d %H:%i:%S'),intensity,lat,lng,speed_of_movement,movement_direction,pressure,max_wind_speed,status FROM typhoon_path order by tc_id,id")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['tc_id'] = r[1]
        tmp['analysis_time'] = r[2]
        tmp['intensity'] = r[3]
        tmp['lat'] = r[4]
        tmp['lng'] = r[5]
        tmp['speed_of_movement'] = r[6]
        tmp['movement_direction'] = r[7]
        tmp['pressure'] = r[8]
        tmp['max_wind_speed'] = r[9]
        tmp['status'] = r[10]
        
        tmp['imageURL'] = "../svg/typhoon.svg"
        tmp['width'] = 30
        tmp['label'] = 'Typhoon'
        typhoonPathList[c] = tmp
        c=c+1
        
    earthquakeList = OrderedDict();
    cur.execute("SELECT id,DATE_FORMAT(datetime,'%Y-%m-%d %H:%i:%S'),latitude,longitude,depth,mag,region,status FROM earthquake ORDER BY datetime DESC")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['datetime'] = r[1]
        tmp['latitude'] = r[2]
        tmp['longitude'] = r[3]
        tmp['depth'] = r[4]
        tmp['mag'] = r[5]
        tmp['region'] = r[6]
        tmp['status'] = r[7]
        earthquakeList[c] = tmp
        c=c+1 
    
    cur.close()
    conn.close()
    
    returnData = OrderedDict(); 
    returnData['typhoonList'] = typhoonList    
    returnData['typhoonPathList'] = typhoonPathList
    returnData['earthquakeList'] = earthquakeList
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response  

@app.route("/eventDelete", methods=['GET'])
def eventDelete():
    eventid = request.args.get('eventid')
    """
    connstr_dev = "SQE_AP/TSQEAP2020@10.56.172.113:1521/TJNCOMB"
    schema_dev = "SCMP_ADM"

    # 2021/1 新的Oracle19c
    connstr_pro = "SQE_AP/PSQEAP2020@10.56.172.83:1521/PPMCDB"
    schema_pro = "PPMC_ADM"
    """
    
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    cur.execute("SELECT SQE_ID,env FROM event_manual where id=%s",(eventid))
    for r in cur :
        SQE_ID = r[0]
        env = r[1]
        
    if str(env) == '0' : #開發
        connstr = connstr_dev
        schema = schema_dev
    elif str(env) == '1' : #正式
        connstr = connstr_pro
        schema = schema_pro
        
    conO = cx_Oracle.connect(connstr,encoding = "UTF-8", nencoding = "UTF-8")
    curO = conO.cursor()    
     
    
    #20201221 改成直接刪除
    cur.execute("delete from event_manual where id=%s",(eventid))
    
    curO.execute("update "+schema+".MAP_DISASTER_H set FLAG=2 where ID=:v",{'v': SQE_ID})
    #print('eventid:',eventid,' , SQE_ID:',SQE_ID)
    cur.execute("commit")
    curO.execute("commit")    
    
    cur.close()
    conn.close()
    
    curO.close()
    conO.close()
    
    response = jsonify({'result':0})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/getEvent", methods=['GET'])
def getEvent():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
     
    # Event Manual List
    eventmanuallist = OrderedDict();
    cur.execute("SELECT id,country,city,eventname,SQE_ID,env from event_manual where status=0")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['country'] = r[1]
        tmp['city'] = r[2]
        tmp['eventname'] = r[3]
        tmp['SQE_ID'] = r[4]
        tmp['env'] = r[5]
        eventmanuallist[c] = tmp
        c=c+1
    cur.close()
    conn.close()
    
    returnData = OrderedDict(); 
    """
    returnData['eventlist'] = listDict    
    returnData['eventtypeSet'] = eventtypeSet
    returnData['countrySet'] = countrySet
    returnData['eventname'] = eventnameSet
    returnData['eventmap'] = eventmap
    """
    returnData['eventmanuallist'] = eventmanuallist
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 

@app.route("/checkCountryCity", methods=['GET'])
def checkCountryCity():   
    country = request.args.get('country')
    city = request.args.get('city')      
    #print('country:',country,' ,city:',city)    
    geolocator = Nominatim(user_agent="GG")
    try :
        location = geolocator.geocode(country+city) 
        #print((location.address,location.longitude,location.latitude ))
        response = jsonify({'result':0,'address':location.address,'longitude': location.longitude,'latitude':location.latitude})
    except Exception as e:
        #print('GeoPY:'+str(e))
        response = jsonify({'result':1})
    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/eventaddmanual", methods=['GET'])
def eventaddmanual():   
    country = request.args.get('country')
    city = request.args.get('city')   
    eventname = request.args.get('eventname') 
    env = request.args.get('env')
    #print('country:',country,' ,city:',city,' ,eventname:',eventname)
    
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    cur.execute("insert into event_manual(country,city,eventname,env)values(%s,%s,%s,%s)",(country,city,eventname,env))    
    cur.execute("commit")
    cur.execute("SELECT LAST_INSERT_ID()")
    id = cur.fetchone()[0];
    
    cur.close()
    conn.close()
    response = jsonify({'LAST_INSERT_ID':id})    
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/eventSubscribe", methods=['GET'])
def eventSubscribe():    
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    #eventidlist = request.args.get('eventidlist')
    eventidlist_m = request.args.get('eventidlist_m')
    PERNR = request.args.get('PERNR')
    userChineseName = request.args.get('userChineseName')
    env = request.args.get('env')
    
    if str(env) == '0' : #開發
        connstr = connstr_dev
        schema = schema_dev
    elif str(env) == '1' : #正式
        connstr = connstr_pro
        schema = schema_pro
        
    conO = cx_Oracle.connect(connstr,encoding = "UTF-8", nencoding = "UTF-8")
    curO = conO.cursor() 
    
    #print('eventidlist_m:',eventidlist_m, ' ,PERNR:',PERNR,' ,userChineseName:',userChineseName)
    
    eventIdAddMappList = []
    eventIdRemoveMappList = []
    # A.依據勾選的結果來增加對接資料
    if eventidlist_m != '':
        for eventid in eventidlist_m.split(',') :
            cur.execute("select eventname,country,city,SQE_ID from event_manual where id=%s",(eventid))
            for r in cur : 
                eventname = r[0] 
                country = r[1]
                city = r[2]
                SQE_ID = r[3]
            #print(eventid,' ',eventname,' ',country,' ',city,' SQE_ID:',SQE_ID)
            FLAG = '2'
            # step1 判斷是否已經對接過
            #print('step1 判斷是否已經對接過')
            if SQE_ID > 0 : # 先到MIS地圖資料庫，確認該筆ID是否還有效，若有效則不動作，若無效則塞入                
                curO.execute("select FLAG from "+schema+".MAP_DISASTER_H where ID=:v",{'v': SQE_ID})
                FLAG = curO.fetchone()
                if FLAG is not None :
                    FLAG = FLAG[0]
            #print(' FLAG:',FLAG)
            if FLAG != '1' : # FLAG = 2 或 沒這筆SQE_ID
                eventIdAddMappList.append(str(eventid))

                # step2 取得PPMC_ADM.MAP_DISASTER_H最新ID    
                curO.execute("SELECT NVL(MAX(ID),0)+1 FROM "+schema+".MAP_DISASTER_H") 
                SQE_ID = curO.fetchone()[0];
                #print('step2 取得 MAP_DISASTER_H最新ID, SQE_ID=',SQE_ID)
            
                # step3 insert MAP_DISASTER_H
                startdate = time.strftime("%Y%m%d", time.localtime())
                curO.execute("insert into "+schema+".MAP_DISASTER_H(ID,EVENT,DATETIME,CREATION_DATE,CREATEBY,FLAG)values(:i,:e,to_date(:d, 'yyyymmdd'),sysdate,:c,1)",{'i':SQE_ID,'e':country+city+eventname,'d':startdate,'c':'idap-'+userChineseName})

                # step4 update event SQE_ID
                cur.execute("update event_manual set SQE_ID=%s where id=%s",(SQE_ID,eventid))
            
                # step5 insert MAP_DISASTER_AREA
                #print('step4 ',country,' ',city) 
                curO.execute("insert into "+schema+".MAP_DISASTER_AREA (ID,AREA1,COUNTRY,CREATION_DATE,CREATEBY) values(:i,:a,:c,sysdate,'idap')",{'i':SQE_ID,'a':city,'c':country})                 
            else :
                print('FLAG = 1，已經對接過，不須重新對接!')
    
        # B.確認清除的反勾選的項目
        #print('step5 確認清除的勾選的項目')
        cur.execute("select id,SQE_ID from event_manual where SQE_ID>0 and id not in ("+eventidlist_m+")")
        if cur.rowcount > 0 :
            for r in cur : 
                eventid = r[0]
                SQE_ID = r[1]
                eventIdRemoveMappList.append(str(eventid))
                # 20201222,張瑞明，當MAP_DISASTER_H set FLAG=2時，要記錄PERNR，userChineseName
                curO.execute("update "+schema+".MAP_DISASTER_H set FLAG=2,DELETE_EMPNO=:de, DELETE_NAME=:dn where ID=:v",{'de':PERNR,'dn':userChineseName,'v': SQE_ID})
            cur.execute("update event_manual set SQE_ID=0 where SQE_ID>0 and id not in ("+eventidlist_m+")")
            
    # C.全部未勾選，確認全部清除
    else :
        #print('C.全部未勾選，確認全部清除')
        cur.execute("select id,SQE_ID from event_manual where SQE_ID>0")
        if cur.rowcount > 0 :
            for r in cur : 
                eventid = r[0]
                SQE_ID = r[1]
                eventIdRemoveMappList.append(str(eventid))
                curO.execute("update "+schema+".MAP_DISASTER_H set FLAG=2,DELETE_EMPNO=:de, DELETE_NAME=:dn where ID=:v",{'de':PERNR,'dn':userChineseName,'v': SQE_ID})
                #print('  de:',PERNR,' dn:',userChineseName,' SQE_ID:', SQE_ID)
            cur.execute("update event_manual set SQE_ID=0 where SQE_ID>0")
            #print("update event_manual")
    
        
    cur.execute("commit")
    curO.execute("commit")    
    
    # 20201223 mapp        
    #print('eventIdAddMappList:',len(eventIdAddMappList),' ',eventIdAddMappList)
    #print('eventIdRemoveMappList:',len(eventIdRemoveMappList),' ',eventIdRemoveMappList)
    if len(eventIdAddMappList) > 0 or len(eventIdRemoveMappList) > 0 :
        connect_mapp(eventIdAddMappList,eventIdRemoveMappList,env)
        
    cur.close()
    conn.close()
    
    curO.close()
    conO.close()
    
    response = jsonify({'result':0})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/getEventSubscribe", methods=['GET'])
def getEventSubscribe():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    eventidlist = [];
    
    cur.execute("select id from event where SQE_ID>0")
    if cur.rowcount > 0 : 
        for r in cur :            
            eventidlist.append(r[0])
    cur.close()
    conn.close()        
    response = jsonify({'eventidlist':eventidlist});         
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response    
    
@app.route("/getEventNews", methods=['GET'])
def getEventNews():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    eventid = request.args.get('eventid')
    returnData = OrderedDict();
    cur.execute("SELECT title,publishdate,url FROM eventnews WHERE eventid=%s and status=0 ORDER BY publishdate desc",(eventid))
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['title'] = r[0]
        tmp['publishdate'] = r[1]
        tmp['url'] = r[2]
        returnData[c] = tmp
        c=c+1
    
    cur.close()
    conn.close()
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
@app.route("/getNewsList", methods=['GET'])
def getNewsList():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    returnData = OrderedDict();
    listDict = OrderedDict();
    web = request.args.get('web')
    cur.execute("SELECT id,title,publishdate FROM news where status=0 and content is not null and content <> '' and web=%s order by publishdate desc",(web))
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['title'] = r[1]
        tmp['publishdate'] = r[2]
        listDict[c] = tmp
        c=c+1
    
    spacyLabel = {"DATE":{},"EVENT":{},"LOC":{},"ORG":{},"PERSON":{},"TIME":{},"FAC":{},"GPE":{}};

    cur.execute("SELECT spacy_result FROM news where status=0 and spacy_result is not null and spacy_result <> '' and web=%s",(web))
    for r in cur :
        spacy_result = json.loads(r[0])  
        for i in range(0,len(spacy_result)) :
            label = spacy_result[i][1]
            term = spacy_result[i][0]
            if label in spacyLabel :
                if term in spacyLabel[label] :
                    spacyLabel[label][term] = spacyLabel[label][term] + 1
                else :
                    spacyLabel[label].update({term : 1})        
    cur.close()
    conn.close()
    
    returnData['list'] = listDict    
    returnData['spacyLabel'] = spacyLabel 
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 


@app.route("/getNewsContent", methods=['GET'])
def getNewsContent():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    returnData = OrderedDict();
    id = request.args.get('id')
    cur.execute('SELECT content,publishdate,url,nltk_result,spacy_result,title FROM news where id=%s',(id))
    
    for r in cur :        
        returnData['content'] = r[0]
        returnData['publishdate'] = r[1]
        returnData['url'] = r[2]
        returnData['nltk_result'] = r[3]
        returnData['spacy_result'] = r[4]
        returnData['title'] = r[5]        
    cur.close()
    conn.close()
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 

@app.route("/getNewsNer", methods=['GET'])
def getNewsNer():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    
    returnData = OrderedDict();
    
    nametypeList = {'PERSON':'人名','NORP':'團體','FAC':'建築物','ORG':'公司機構','GPE':'行政單位','LOC':'地點','PRODUCT':'產品','EVENT':'事件','WORK_OF_ART':'物品','LAW':'法律'} 
    #nametypeList = {'PERSON':'人名','NORP':'團體','EVENT':'事件'} 
    for d in nametypeList :
        dictTmp = OrderedDict();
        #print(d,' ',nametypeList[d])
        cur.execute("select publishdate,entity, c from (SELECT publishdate,entity,sum(count) c FROM news_ner where web in ('nikkei','hket','worldjournal','epochtimes','plataformamedia','kyodonews','rfi','storm','crossing','thenewslens','newtalk','worldjournal') and nametype =%s GROUP by entity,publishdate) a where c >10 ORDER by publishdate desc,c desc limit 30",(d))
        c=0
        for r in cur :
            tmp = OrderedDict()
            tmp['publishdate'] = int(r[0])
            tmp['entity'] = r[1]
            tmp['count'] = int(r[2])
            #print(r[0],' ',r[1],' ',r[2]) 
            dictTmp[c] = tmp
            c=c+1
        returnData[nametypeList[d]] = dictTmp    
    
    cur.close()
    conn.close()
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 

@app.route("/getDisaster", methods=['GET'])
def getDisaster():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()    
    
    # Event Manual List
    eventmanuallist = OrderedDict();
    cur.execute("SELECT id,country,city,eventname,SQE_ID,env from event_manual where status=0")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['country'] = r[1]
        tmp['city'] = r[2]
        tmp['eventname'] = r[3]
        tmp['SQE_ID'] = r[4]
        tmp['env'] = r[5]
        eventmanuallist[c] = tmp
        c=c+1
    
    # eventtypeList
    # 20210127 eventtypeList改成maker全球 
    eventtypeList = OrderedDict();    
    cur.execute("select g.eventtype,count(1) c from \
        (select a.eventtype,a.newsid from news_disaster a left join \
        (select NAME_ch,CITY from MAP_AML_MAKER_FOR_MDM_V_4SQE where city is not null GROUP by NAME_ch,city) b \
        on b.NAME_ch=a.country and b.CITY=a.city where b.city is not null) g \
        left join news_daily c on g.newsid=c.id GROUP by g.eventtype order by c desc") 
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['eventtype'] = r[0]
        tmp['count'] = r[1]
        eventtypeList[c] = tmp
        c=c+1     
    
    # 20201207 makerEventtypeList
    # 20210127 改成eventtypeList_tw，台灣maker
    eventtypeList_tw = OrderedDict(); 
    cur.execute("select g.eventtype,count(1) c from (select a.eventtype,a.newsid from news_disaster a left join (select NAME_ch,CITY from MAP_AML_MAKER_FOR_MDM_V_4SQE where NAME_ch ='台灣' and city is not null GROUP by NAME_ch,city) b         on b.NAME_ch=a.country and b.CITY=a.city where a.country='台灣' and b.city is not null) g left join news_daily c on g.newsid=c.id GROUP by g.eventtype order by c desc")
    
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['eventtype'] = r[0]
        tmp['count'] = r[1]
        eventtypeList_tw[c] = tmp
        c=c+1     
    
    # mainList
    # 20210127 改成全球maker
    mainList = OrderedDict();
    cur.execute("select g.country,g.city,g.eventtype,count(1) c from\
        (select a.eventtype,a.newsid,a.country,a.city from news_disaster a left join\
        (select NAME_ch,CITY from MAP_AML_MAKER_FOR_MDM_V_4SQE where city is not null GROUP by NAME_ch,city) b \
        on b.NAME_ch=a.country and b.CITY=a.city where b.city is not null) g left join news_daily c on g.newsid=c.id \
        GROUP by g.country,g.city,g.eventtype order by eventtype,c desc")
    c=0
    eventtypeTmp = ''
    mainTmp = OrderedDict();
    uniqueCity = []
    for r in cur : 
        if c != 0 and eventtypeTmp != r[2] :
            mainList[eventtypeTmp] = mainTmp
            #eventtypeTmp = r[2]
            c=0            
            mainTmp = OrderedDict();
        eventtypeTmp = r[2]    
        tmp = OrderedDict()
        tmp['country'] = r[0]
        tmp['city'] = r[1]
        tmp['count'] = r[3]
        if tmp['city'] not in uniqueCity:
            uniqueCity.append(tmp['city'])
        mainTmp[c] = tmp
        c=c+1       
    mainList[eventtypeTmp] = mainTmp # 最後一個    
    
    # 該城市的廠商數量
    makerCount = OrderedDict();
    queryCity = "'"+"','".join(uniqueCity)+"'"      
    
    cur.execute("select city,count(1) c from(SELECT DISTINCT city, SYSTEM_FACTORY_NAME FROM MAP_AML_MAKER_FOR_MDM_V_4SQE WHERE city in ("+queryCity+")) a group by city order by c desc")
    
    for r in cur :
        makerCount[r[0]] = r[1]
        
    # 20201207 makerMainList
    # 20210127 改成mainList_tw，台灣maker
    mainList_tw = OrderedDict();
    cur.execute("select g.country,g.city,g.eventtype,count(1) c from (select a.eventtype,a.newsid,a.country,a.city from\
        news_disaster a left join\
        (select NAME_ch,CITY from MAP_AML_MAKER_FOR_MDM_V_4SQE where NAME_ch ='台灣' and city is not null GROUP by NAME_ch,city) b\
        on b.NAME_ch=a.country and b.CITY=a.city where a.country='台灣' and b.city is not null) g \
        left join news_daily c on g.newsid=c.id GROUP by g.country,g.city,g.eventtype order by eventtype,c desc")    
    c=0
    eventtypeTmp = ''
    mainTmp = OrderedDict();    
    for r in cur : 
        if c != 0 and eventtypeTmp != r[2] :
            mainList_tw[eventtypeTmp] = mainTmp
            c=0            
            mainTmp = OrderedDict();
        eventtypeTmp = r[2]    
        tmp = OrderedDict()
        tmp['country'] = r[0]
        tmp['city'] = r[1]
        tmp['count'] = r[3]
        
        mainTmp[c] = tmp
        c=c+1       
    mainList_tw[eventtypeTmp] = mainTmp # 最後一個    
        
    # newsList 
    # 20210127 改成全球maker
    newsList = OrderedDict();
    cur.execute("select newsid,country,city,eventtype,publishdate,url,title from \
        (select a.eventtype,a.newsid,a.country,a.city from news_disaster a left join \
        (select NAME_ch,CITY from MAP_AML_MAKER_FOR_MDM_V_4SQE where city is not null GROUP by NAME_ch,city) b\
        on b.NAME_ch=a.country and b.CITY=a.city where b.city is not null) g left join news_daily c on g.newsid=c.id\
        order by eventtype,country,city, publishdate desc")
    c=0
    country_city_eventtype = ''
    newsTmp = OrderedDict()
    for r in cur :
        if c != 0 and country_city_eventtype != r[1]+'-'+r[2]+'-'+r[3] :
            newsList[country_city_eventtype] = newsTmp 
            c=0            
            newsTmp = OrderedDict();
        country_city_eventtype = r[1]+'-'+r[2]+'-'+r[3]    
        tmp = OrderedDict()
        tmp['newsid'] = r[0]
        tmp['publishdate'] = r[4]
        tmp['url'] = r[5]
        tmp['title'] = r[6]
        newsTmp[c] = tmp
        c=c+1  
    newsList[country_city_eventtype] = newsTmp # 最後一個     
    
    # makerNewsList  20201208  
    # 20210127 改成newsList_tw，台灣maker
    newsList_tw = OrderedDict();
    cur.execute("select newsid,country,city,eventtype,publishdate,url,title from\
        (select a.eventtype,a.newsid,a.country,a.city from news_disaster a left join \
        (select NAME_ch,CITY from MAP_AML_MAKER_FOR_MDM_V_4SQE where NAME_ch ='台灣' and city is not null GROUP by NAME_ch,city) b \
        on b.NAME_ch=a.country and b.CITY=a.city where a.country='台灣' and b.city is not null) g \
        left join news_daily c on g.newsid=c.id\
        order by eventtype,country,city, publishdate desc")
    c=0
    country_city_eventtype = ''
    newsTmp = OrderedDict()
    for r in cur :
        if c != 0 and country_city_eventtype != r[1]+'-'+r[2]+'-'+r[3] :
            newsList_tw[country_city_eventtype] = newsTmp 
            c=0            
            newsTmp = OrderedDict();
        country_city_eventtype = r[1]+'-'+r[2]+'-'+r[3]    
        tmp = OrderedDict()
        tmp['newsid'] = r[0]
        tmp['publishdate'] = r[4]
        tmp['url'] = r[5]
        tmp['title'] = r[6]
        newsTmp[c] = tmp
        c=c+1  
    newsList_tw[country_city_eventtype] = newsTmp # 最後一個     
    
    # earthquake  20210111  
    earthquakeList = OrderedDict();
    cur.execute("SELECT id,`index`,DATE_FORMAT(datetime,'%Y-%m-%d %H:%i:%S'),region,mag,creationdate FROM earthquake_tw ORDER BY datetime DESC")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['index'] = r[1]
        tmp['datetime'] = r[2]
        tmp['city'] = r[3]
        #tmp['depth'] = r[4]
        tmp['mag'] = r[4]
        tmp['creationdate'] = r[5]
        earthquakeList[c] = tmp
        c=c+1
        
    cur.close()
    conn.close()
    
    returnData = OrderedDict();    
    
    returnData['eventmanuallist'] = eventmanuallist
    returnData['eventtypeList'] = eventtypeList
    returnData['mainList'] = mainList
    returnData['newsList'] = newsList
    
    returnData['eventtypeList_tw'] = eventtypeList_tw
    returnData['mainList_tw'] = mainList_tw
    returnData['newsList_tw'] = newsList_tw
    
    returnData['earthquakeList'] = earthquakeList
    
    returnData['makerCount'] = makerCount
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/getMakerByCity", methods=['GET'])
def getMakerByCity():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    
    city = request.args.get('city')
    makerList = OrderedDict();
    #cur.execute("SELECT SYSTEM_FACTORY_NAME,CATEGORY_L1,CATEGORY_L2 FROM MAP_AML_MAKER_FOR_MDM_V_4SQE where CITY=%s ORDER by MAKER_NO",(city))
    cur.execute("SELECT DISTINCT SYSTEM_FACTORY_NAME FROM MAP_AML_MAKER_FOR_MDM_V_4SQE where CITY=%s ORDER by MAKER_NO",(city))
     
    #SELECT DISTINCT SYSTEM_FACTORY_NAME FROM MAP_AML_MAKER_FOR_MDM_V_4SQE WHERE city in ('高雄')    
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['SYSTEM_FACTORY_NAME'] = r[0]
        #tmp['CATEGORY_L1'] = r[1]
        #tmp['CATEGORY_L2'] = r[2]
        makerList[c] = tmp
        c=c+1  
    
    cur.close()
    conn.close()
    
    returnData = OrderedDict();
    returnData['makerList'] = makerList    
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 20210322 keyword_subscribeAmin #############################################################################
@app.route("/keyword_subscribeAmin", methods=['GET'])
def keyword_subscribeAmin():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()

# 20210315 deleteSubscribe #############################################################################
@app.route("/deleteSubscribe", methods=['GET'])
def deleteSubscribe():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    
    id = request.args.get('id')
    #print('deleteSubscribe id=',id)
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    updatetime = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')
    
    cur.execute("update news_keyword_subscribe set status=2 , updatetime=%s where id=%s",(updatetime,id))
    cur.execute("commit")
    cur.close()
    conn.close()
    
    returnData = OrderedDict();
    returnData['result'] = 0
    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 20210309 get_keyword_subscribe #############################################################################
@app.route("/get_keyword_subscribe", methods=['GET'])
def get_keyword_subscribe():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    
    PERNR = request.args.get('PERNR')
    cur.execute("select id,keyword,keyword_tw,language,PERNRList,chatsnList,useraccount,apikey,team_sn,DATE_FORMAT(creationdate,'%Y-%m-%d %H:%i:%S') from news_keyword_subscribe where PERNR='"+PERNR+"' and status=0 order by id desc")
    if cur.rowcount > 0 :        
        subscribe_list = OrderedDict();
        c = 0
        for r in cur :
            tmp = OrderedDict()
            tmp['id'] = r[0]
            tmp['keyword'] = r[1]
            tmp['keyword_tw'] = r[2]
            tmp['language'] = r[3]
            tmp['PERNRList'] = r[4]
            tmp['chatsnList'] = r[5]
            tmp['useraccount'] = r[6]
            tmp['apikey'] = r[7]
            tmp['team_sn'] = r[8]
            tmp['creationdate'] = r[9]
            subscribe_list[c] = tmp
            c=c+1
    else :
        subscribe_list = 0;
        
    cur.close()
    conn.close()
    
    returnData = OrderedDict();
    returnData['subscribe_list'] = subscribe_list    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 20210308 keyword_subscribe #############################################################################
@app.route("/keyword_subscribe", methods=['GET'])
def keyword_subscribe():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    
    # 先將簡中轉繁中
    keyword = gl_translator(request.args.get('keyword').strip(), 'zh-cn', 'zh-tw')
    keyword_tw = keyword
    language = request.args.get('language')
    PERNR = request.args.get('PERNR')
    userChineseName = request.args.get('userChineseName')
    PERNRList = request.args.get('PERNRList').strip()
    chatsnList = request.args.get('chatsnList').strip()
    subscribeEditID = request.args.get('subscribeEditID').strip() #0表示新增，非0表示修改
    
    useraccount = request.args.get('useraccount').strip()
    apikey = request.args.get('apikey').strip()
    team_sn = None if request.args.get('team_sn').strip() is '' else request.args.get('team_sn').strip();
    
    #print(type(subscribeEditID))
    #print('keyword:',keyword,', keyword_tw:',keyword_tw,', PERNR:',PERNR,', userChineseName:',userChineseName,', PERNRList:',PERNRList,' , chatsnList:',chatsnList,' , subscribeEditID:',subscribeEditID)

    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    creationdate = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')
    result = 0;
    if str(subscribeEditID) == '0' :
        cur.execute("select * from news_keyword_subscribe where PERNR=%s and keyword=%s and language=%s and status=0",(PERNR,keyword,language))
        if cur.rowcount == 0 : 
            cur.execute("insert into news_keyword_subscribe(keyword,keyword_tw,language,PERNR,userChineseName,PERNRList,chatsnList,useraccount,apikey,team_sn,creationdate,updatetime)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(keyword,keyword_tw,language,PERNR,userChineseName,PERNRList,chatsnList,useraccount,apikey,team_sn,creationdate,creationdate))            
            result = 0;
        else :
            result = 1; # 重複訂閱
    else :
        cur.execute("update news_keyword_subscribe set keyword=%s,keyword_tw=%s,PERNRList=%s,chatsnList=%s,useraccount=%s,apikey=%s,team_sn=%s,updatetime=%s where id=%s",(keyword,keyword_tw,PERNRList,chatsnList,useraccount,apikey,team_sn,creationdate,subscribeEditID))
    cur.execute("commit")    
    # keyword	keyword_tw	language	PERNR	userChineseName	PERNRList	chatsnList	creationdate	updatetime
    
    cur.close()
    conn.close()
    
    returnData = OrderedDict();
    returnData['result'] = result    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 20210323 get_keywordsearch_log_admin #############################################################################
@app.route("/get_keywordsearch_log_admin", methods=['GET'])
def get_keywordsearch_log_admin():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    #PERNR = request.args.get('PERNR')
    
    keywordsearch_log = OrderedDict();
    cur.execute("SELECT keyword,keyword_tw,language,resultCount,DATE_FORMAT(creationdate,'%Y-%m-%d %H:%i:%S'),PERNR,userChineseName FROM news_keyword_log ORDER BY id DESC")
    if cur.rowcount > 0 :
        c = 0
        for r in cur :
            tmp = OrderedDict()
            tmp['keyword'] = r[0]
            tmp['keyword_tw'] = r[1]
            tmp['language'] = r[2]
            tmp['resultCount'] = r[3]
            tmp['creationdate'] = r[4]
            tmp['PERNR'] = r[5]
            tmp['userChineseName'] = r[6]            
            keywordsearch_log[c] = tmp
            c=c+1 
    
    cur.close()
    conn.close()
    
    returnData = OrderedDict();
    returnData['keywordsearch_log'] = keywordsearch_log    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 20210308 get_keywordsearch_log #############################################################################
@app.route("/get_keywordsearch_log", methods=['GET'])
def get_keywordsearch_log():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    PERNR = request.args.get('PERNR')
    
    keywordsearch_log = OrderedDict();
    cur.execute("SELECT keyword,keyword_tw,language,resultCount,DATE_FORMAT(creationdate,'%Y-%m-%d %H:%i:%S') FROM news_keyword_log where PERNR='"+PERNR+"' ORDER BY id DESC limit 30")
    if cur.rowcount > 0 :
        c = 0
        for r in cur :
            tmp = OrderedDict()
            tmp['keyword'] = r[0]
            tmp['keyword_tw'] = r[1]
            tmp['language'] = r[2]
            tmp['resultCount'] = r[3]
            tmp['creationdate'] = r[4]
            keywordsearch_log[c] = tmp
            c=c+1 
    
    cur.close()
    conn.close()
    
    returnData = OrderedDict();
    returnData['keywordsearch_log'] = keywordsearch_log    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
   
    
# 20210301 keyword_search #######################################################################################
@app.route("/keyword_search", methods=['GET'])
def keyword_search():
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    
    keywordOrigin = request.args.get('keyword')
    #keywordTmp = keywordOrigin.split('+')
    keyword_tw = request.args.get('keyword_tw')
    language = request.args.get('language')
    if language == 'ja' :
        language = 'jp'
    PERNR = request.args.get('PERNR')
    userChineseName = request.args.get('userChineseName')
    print('keywordOrigin:',keywordOrigin,' ',keyword_tw,' ',language,' ',PERNR,' ',userChineseName)
     
    """
    query_str = ''
    
    if len(keywordTmp) > 1 :
        for keyword in keywordTmp :
            keyword = keyword.strip()
            print('keyword_search:'+keyword)
            if query_str == '' :
                query_str = "content like '%"+keyword+"%'"
            else :
                query_str = query_str+" and content like '%"+keyword+"%'"
    else :
        keyword = keywordTmp[0].strip()
        query_str = "content like '%"+keyword+"%'"
    """    
    query_str = convertKeywordToSQLStatement(keywordOrigin)
    print('keyword_search : query_str:'+query_str)
    newsList = OrderedDict();
    
    if language == 'tw' :
        cur.execute("SELECT id,web,title,content,publishdate,url FROM news_daily WHERE status=0 and content is not null and "+query_str+" ORDER BY publishdate desc")    
    else :
        cur.execute("SELECT id,web,title,content,publishdate,url FROM news_daily_source WHERE status=0 and content is not null and "+query_str+" and language='"+language+"' ORDER BY publishdate desc")    
    resultCount=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['web'] = r[1]
        tmp['title'] = r[2]
        tmp['content'] = r[3]
        tmp['publishdate'] = r[4]
        tmp['url'] = r[5]
        newsList[resultCount] = tmp
        resultCount=resultCount+1  
    #print('resultCount:',resultCount)
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    creationdate = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')
    cur.execute("insert into news_keyword_log(keyword,keyword_tw,language,PERNR,userChineseName,resultCount,creationdate)values(%s,%s,%s,%s,%s,%s,%s)",(keywordOrigin,keyword_tw,language,PERNR,userChineseName,resultCount,creationdate))
    cur.execute("commit")
    
    cur.close()
    conn.close()
    
    returnData = OrderedDict();
    returnData['newsList'] = newsList    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 20210301 keyword_search_realtime_translate  ################################################################
@app.route("/realtime_translate", methods=['GET'])
def realtime_translate() :
    keywordTmp = request.args.get('keyword').split('+')
    #keywordTmp = request.args.get('keyword').split(' ')
    lang_src = request.args.get('lang_src')
    lang_tgt = request.args.get('lang_tgt')
    result = ''
    if len(keywordTmp) > 1 :
        for keyword in keywordTmp :
            keyword = keyword.strip()
            print('realtime_translate:'+keyword)
            if result == '' :
                result = gl_translator(keyword, lang_src, lang_tgt)
            else :
                result = result+"+"+gl_translator(keyword, lang_src, lang_tgt).strip()
    else :
        keyword = keywordTmp[0].strip()
        result = gl_translator(keyword, lang_src, lang_tgt)
    returnData = OrderedDict();
    returnData['result'] = result    
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
def gl_translator(text, lang_src, lang_tgt) :
    #print('gl_translator:', text,lang_src,lang_tgt)
    url_suffix_list = ['ac','ad','ae','al','am','as','at','az','ba','be','bf','bg','bi','bj','bs','bt','by','ca','cat','cc','cd','cf','cg','ch','ci','cl','cm','cn','co.ao','co.bw','co.ck','co.cr','co.id','co.il','co.in','co.jp','co.ke','co.kr','co.ls','co.ma','co.mz','co.nz','co.th','co.tz','co.ug','co.uk','co.uz','co.ve','co.vi','co.za','co.zm','co.zw','co','com.af','com.ag','com.ai','com.ar','com.au','com.bd','com.bh','com.bn','com.bo','com.br','com.bz','com.co','com.cu','com.cy','com.do','com.ec','com.eg','com.et','com.fj','com.gh','com.gi','com.gt','com.hk','com.jm','com.kh','com.kw','com.lb','com.lc','com.ly','com.mm','com.mt','com.mx','com.my','com.na','com.ng','com.ni','com.np','com.om','com.pa','com.pe','com.pg','com.ph','com.pk','com.pr','com.py','com.qa','com.sa','com.sb','com.sg','com.sl','com.sv','com.tj','com.tr','com.tw','com.ua','com.uy','com.vc','com.vn','com','cv','cx','cz','de','dj','dk','dm','dz','ee','es','eu','fi','fm','fr','ga','ge','gf','gg','gl','gm','gp','gr','gy','hn','hr','ht','hu','ie','im','io','iq','is','it','je','jo','kg','ki','kz','la','li','lk','lt','lu','lv','md','me','mg','mk','ml','mn','ms','mu','mv','mw','ne','nf','nl','no','nr','nu','pl','pn','ps','pt','ro','rs','ru','rw','sc','se','sh','si','sk','sm','sn','so','sr','st','td','tg','tk','tl','tm','tn','to','tt','us','vg','vu','ws']
    #url_suffix_list = ['us','cn','tw']
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
    #print(content_tw)        
    return content_tw

##################################################################################################
# 20201208 mapp
def mapppost_content(useraccount,apikey,chatsn,content):
    content_utf8 = content.encode("UTF-8")#轉UTF8
    content_utf8_url = urllib.parse.quote_plus(content_utf8)#轉URL
    url = "http://mapp.local/teamplus_innolux/API/IMService.ashx"
    payload = "ask=sendChatMessage&account={}&api_Key={}&chat_sn={}&content_type=1&msg_content={}&file_show_name=&undefined=".format(useraccount,apikey,chatsn,content_utf8_url)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    #print('mapppost_content: ',response.text)
    
    result = json.loads(response.text)
                
    if not result['IsSuccess'] :
        return [3,result['ErrorCode'],result['IsSuccess'],result['Description']]
    
    return [0,result['ErrorCode'],result['IsSuccess'],result['Description']]
     
def connect_mapp(eventIdAddMappList,eventIdRemoveMappList,env):
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    yearmonth = date.today().strftime('%Y%m%d')   
        
    if str(env) == '0' : #開發
        chatsnList = chatsn_dev.split(',')
        content = '[測試][突發事件警訊]\n'+yearmonth+'\n';
        url = 'http://tscmp.cminl.oa/?type=emerg&eventid='
    elif str(env) == '1' : #正式
        chatsnList = chatsn_pro.split(',')
        content = '[正式][突發事件警訊]\n'+yearmonth+'\n';
        url = 'http://pscmp.cminl.oa/?type=emerg&eventid='
    # 文字部分
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    currentDateTime = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')  # 轉換時區 -> 東八區
    
    mappCount=1
    #print('  eventIdAddMappList:',len(eventIdAddMappList) )
    print('  eventIdAddMappList:',eventIdAddMappList )
    # eventIdAddMappList 
    if len(eventIdAddMappList) > 0 :
        cur.execute("select country,city,eventname,SQE_ID from event_manual where id in ("+','.join(eventIdAddMappList)+")")
        for r in cur :
            country = r[0]
            city = r[1]
            eventname = r[2]
            SQE_ID = r[3]
            #print('connect_mapp SQE_ID:',SQE_ID)
            content = content+str(mappCount)+'.[新增]'+country+city+eventname+' '+url+str(SQE_ID)+'\n';
            mappCount = mappCount+1
    
    #print('  eventIdRemoveMappList:',len(eventIdRemoveMappList))
    #print(','.join(eventIdRemoveMappList))
    # eventIdRemoveMappList 
    if len(eventIdRemoveMappList) > 0 :
        cur.execute("select country,city,eventname from event_manual where id in ("+','.join(eventIdRemoveMappList)+")")
        for r in cur :
            country = r[0]
            city = r[1]
            eventname = r[2]
            content = content+str(mappCount)+'.[刪除]'+country+city+eventname+'\n';
            mappCount = mappCount+1
            
    if str(env) == '0' : #開發
        content = content+"採購已啟動供應鏈調查， 相關資訊將顯示於供應鏈地圖平台。"
    elif str(env) == '1' : #正式
        content = content+"採購已啟動供應鏈調查， 相關資訊將顯示於供應鏈地圖平台。"
    #print(content)
    
    for i in range(0,len(chatsnList)) :
        chatsn = chatsnList[i]
        result = mapppost_content(useraccount,apikey,chatsn,content)    
        #print('result')
        #print(result)
        cur.execute("insert into mapp_log(yearmonth,creationdate,status,ErrorCode,IsSuccess,Description)values(%s,now()+INTERVAL 8 HOUR,%s,%s,%s,%s)",(yearmonth,result[0],result[1],result[2],result[3]))                
        cur.execute("COMMIT")    
    cur.close()
    conn.close()
    
# 20210320 航運 ###########################################################
@app.route("/getLogisticNews", methods=['GET'])
def getLogisticNews():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()

    logistic_list = OrderedDict();
    cur.execute("SELECT id,web,title,publishdate,url FROM news_daily WHERE status=0 and content is not null and tag like '%logistic%' ORDER BY publishdate desc")    
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['web'] = r[1]
        tmp['title'] = r[2]
        #tmp['content'] = r[3]
        tmp['publishdate'] = r[3]
        tmp['url'] = r[4] 
        logistic_list[c] = tmp
        c=c+1
        
    cur.close()
    conn.close()
    
    returnData = OrderedDict(); 
    returnData['logistic_list'] = logistic_list
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 20210428 法務 ###########################################################
@app.route("/getLawNews", methods=['GET'])
def getLawNews():
    conn = pymysql.connect(host=host, port=port,user=user, passwd=passwd, db=db)
    cur = conn.cursor()
    law_list = OrderedDict();
    
    keywordList = ['勞資','貪腐','營業秘密','法規','違規','訴訟','專利','合作案','公司風險','投資案','判決','綁標','獨佔','共謀',
                   '佣金','加班','勞基法','檢舉','反托拉斯']
    cur.execute("SELECT id, web,title,publishdate,content FROM i_news WHERE content like '%勞資%' or content like '%貪腐%' or content like '%營業秘密%' or content like '%法規%' or content like '%違規%' or content like '%訴訟%' or content like '%專利%' or content like '%合作案%' or content like '%公司風險%' or content like '%投資案%' or content like '%判決%' or content like '%綁標%' or content like '%獨佔%' or content like '%共謀%' or content like '%佣金%' or content like '%加班%' or content like '%勞基法%' or content like '%檢舉%' or content like '%反托拉斯%' order by publishdate desc,id desc")
    c=0
    for r in cur :
        tmp = OrderedDict()
        tmp['id'] = r[0]
        tmp['web'] = r[1]
        tmp['title'] = r[2]        
        tmp['publishdate'] = r[3]
        tmp['content'] = r[4]
        law_list[c] = tmp
        c=c+1
        
    cur.close()
    conn.close()
    
    returnData = OrderedDict(); 
    returnData['law_list'] = law_list
    response = jsonify(returnData)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 20210326
# 取得 + - | 的所有出現位子
def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

# 20210326
# 將關鍵字組轉成SQL where條件式
def convertKeywordToSQLStatement(keywordOrigin) :
    #keywordList = re.split('\+|-|\|', keywordOrigin)
    keywordList = [x.strip() for x in re.split('\+|-|\|', keywordOrigin)]
    keywordDict = dict.fromkeys(keywordList, '+')
    sqlWhereState = ''
    
    # NOT 
    notList = findOccurrences(keywordOrigin, '-')
    for notIndex in notList :
        #print(notIndex)
        strLen = 0
        c=1
        for keyw in keywordDict :
            strLen = strLen + len(keyw)+1
            #print('strLen:',strLen)
            if strLen > notIndex :
                keywordDict[keywordList[c]] = '-'
                break
            c = c + 1

    # OR        
    orList = findOccurrences(keywordOrigin, '|')
    for orIndex in orList :
        #print(orIndex)
        strLen = 0
        c=1
        for keyw in keywordDict :
            strLen = strLen + len(keyw)+1
            #print('strLen:',strLen)
            if strLen > orIndex :
                keywordDict[keywordList[c]] = '|'
                break
            c = c + 1

    #print(keywordOrigin)        
    #print(keywordDict)
    c = 1
    for key in keywordDict:
        if keywordDict[key] == '+' :
            if c == 1 :
                sqlWhereState = ' content like "%'+key+'%"'
            else :    
                sqlWhereState = sqlWhereState+' and content like "%'+key+'%"'
        elif keywordDict[key] == '|' :
                sqlWhereState = sqlWhereState+' or content like "%'+key+'%"'
        elif keywordDict[key] == '-' :
                sqlWhereState = sqlWhereState+' and content not like "%'+key+'%"'  
        c = c + 1        
        
    return sqlWhereState
    
if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=81)    
    #app.run(host='127.0.0.1', port=85)   
    #app.run(host='10.55.14.206', port=85) 