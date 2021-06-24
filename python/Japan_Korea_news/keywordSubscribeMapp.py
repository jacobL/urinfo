from apscheduler.schedulers.blocking import BlockingScheduler

import pymysql
import time
from datetime import datetime, date,timezone,timedelta

## mapp #######
import urllib
import requests
import json
## selenium ###
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.ie.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
###############

host = '10.55.23.168'
port = 33060
user = 'root'
passwd = "1234"
db = 'idap'

useraccount = 'api_smartpush' 
apikey = '9AE29D27-02F2-016A-11AF-01C9907ABB28'
mappName = 'jacob.liang'
mappPW = 'Ab-123555'

# Step1. 撈取要發送的新聞 
def get_subscribe_news() :
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    cur1 = conn . cursor ()
    cur2 = conn . cursor ()
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    
    #print(dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S'))
    #subscribe_list = OrderedDict();
    cur.execute("SELECT id,keyword,keyword_tw,language,PERNR,PERNRList,chatsnList,useraccount,apikey,team_sn,DATE_FORMAT(updatetime,'%Y-%m-%d %H:%i:%S') FROM news_keyword_subscribe WHERE status=0 order by id")
    if cur.rowcount > 0 :
        for r in cur :
            try :
                subscribeid = r[0]
                keywordOrigin = r[1]
                keywordOrigin_tw = r[2]
                query_str = convertKeywordToSQLStatement(keywordOrigin) 
                language = r[3]
                if language == 'ja' :
                    language = 'jp'

                # 取得的新聞要比建訂閱的時間晚才能mapp
                subscribeUpdatetime = r[10]

                if language == 'tw' :
                    cur1.execute("SELECT id,web,title,'xxx',publishdate,url,content FROM news_daily WHERE status=0 and content is not null and "+query_str+" and creationdate>'"+subscribeUpdatetime+"' ORDER BY id desc")
                else :
                    cur1.execute("SELECT id,web,title,title_tw,publishdate,url,content FROM news_daily_source WHERE status=0 and content is not null and "+query_str+" and language='"+language+"' and creationdate>'"+subscribeUpdatetime+"' ORDER BY id desc")    
                #print(' query_str: ',query_str,' rowcount:',cur1.rowcount)
                newsContent = ''
                newsContentPERNR = ''
                resultCount = 0
                newsidlist = ''          

                for r1 in cur1 :
                    newsid = r1[0]
                    if newsidlist == '':
                        newsidlist = str(newsid)
                    else :
                        newsidlist = newsidlist+','+str(newsid)
                    web = r1[1]
                    title = r1[2]
                    title_tw = r1[3]
                    publishdate = r1[4]
                    url = r1[5] 
                    resultCount=resultCount+1  
                    if language == 'tw' :
                        if web == 'cdnsp' :
                            url = url[:len(url)-1]
                        newsContent = newsContent+str(resultCount)+'. '+title+'('+url+')\n'
                        newsContentPERNR = newsContentPERNR+str(resultCount)+'. '+title+'('+url+') '
                    else :
                        newsContent = newsContent+str(resultCount)+'. (翻譯)'+title_tw+'['+title+']('+url+')\n'
                        newsContentPERNR = newsContentPERNR+str(resultCount)+'. (翻譯)'+title_tw+'['+title+']('+url+') '
                #print(' newsidlist:',newsidlist)
                PERNR = r[4]

                # 有新的新聞要mapp
                if resultCount > 0 :
                    creationdate = dt1.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')  # 轉換時區 -> 東八區

                    # 1. Mapp個人
                    if r[5] != None : 
                        PERNRList = r[5]
                        for PERNR_Name in PERNRList.split(',') :
                            PERNRTmp = PERNR_Name[0:8]
                            Name = PERNR_Name[8:len(PERNR_Name)]
                            #print(' PERNRTmp:',PERNRTmp,Name)  
                            # mapp個人，斷行需要雙斜線。
                            if language == 'tw' :
                                content = Name+r' 您訂閱的關鍵字"'+keywordOrigin+'"有'+str(resultCount)+'筆即時新聞快訊。 '+newsContentPERNR.replace('...','')+'。 ID處Ur-Info即時新聞快訊。 更多快訊: http://pc89600059495s:31080/urinfo/index.html#KeywordSubscribe'
                            else :   
                                content = Name+r' 您訂閱的關鍵字(翻譯)"'+keywordOrigin_tw+'" "'+keywordOrigin+'"有'+str(resultCount)+'筆即時新聞快訊:'+newsContentPERNR.replace('...','')+'。 ID處Ur-Info即時新聞快訊。 更多快訊: http://pc89600059495s:31080/urinfo/index.html#KeywordSubscribe'
                                #content = Name+r' 您訂閱的關鍵字(翻譯) 有'+str(resultCount)+'筆即時新聞快訊:\\n'+newsContentPERNR.replace('...','')+'。 ID處Ur-Info即時新聞快訊。 更多快訊: http://pc89600059495s:31080/urinfo/index.html#KeywordSubscribe'
                            #print(content)    
                            #content = Name+' 您好，以下是關鍵字"'+keyword+'"的'+str(resultCount)+'筆即時新聞快訊。'+newsContent+'ID處Ur-Info即時新聞快訊。更多快訊: http://pc89600059495s:31080/urinfo/index.html#KeywordSubscribe'
                            if len(PERNRTmp) > 4 :
                                mappPERNR(PERNRTmp,content)
                                cur1.execute("insert into news_keyword_subscribe_log (subscribeid,newsidlist,PERNR,creationdate)values(%s,%s,%s,%s)",(subscribeid,newsidlist,PERNRTmp,creationdate))


                    # 2. Mapp即時交談
                    if r[6] != None :     
                        chatsnList = r[6]
                        for chatsn in chatsnList.split(',') : 
                            #print(' chatsn:',chatsn)
                            if language == 'tw' :
                                content = '您訂閱的關鍵字"'+keywordOrigin+'"有'+str(resultCount)+'筆即時新聞快訊:\n'+newsContent+'\nID處Ur-Info即時新聞快訊\n更多快訊: http://pc89600059495s:31080/urinfo/index.html#KeywordSubscribe'
                            else :    
                                content = '您訂閱的關鍵字(翻譯)"'+keywordOrigin_tw+'" "'+keywordOrigin+'"有'+str(resultCount)+'筆即時新聞快訊:\n'+newsContent+'\nID處Ur-Info即時新聞快訊\n更多快訊: http://pc89600059495s:31080/urinfo/index.html#KeywordSubscribe'

                            if len(chatsn) > 4 :
                                result = mappChatsn(chatsn,content)
                                cur1.execute("insert into news_keyword_subscribe_log (subscribeid,newsidlist,chatsn,creationdate, status,ErrorCode,IsSuccess,Description)values(%s,%s,%s,%s, %s,%s,%s,%s)",(subscribeid,newsidlist,chatsn,creationdate, result[0],result[1],result[2],result[3]))

                    # 3. Mapp團隊互動
                    if r[7] != None and r[8] != None and r[9] != None :
                        useraccount = r[7]
                        apikey = r[8]
                        team_sn = str(r[9])
                        #print('3. Mapp團隊互動',useraccount,apikey,team_sn)
                        #mapp_team(useraccount,apikey,team_sn,content,title)
                        if language == 'tw' :
                            cur1.execute("SELECT id,web,title,'xxx',publishdate,url,content FROM news_daily WHERE status=0 and content is not null and "+query_str+" and creationdate>'"+subscribeUpdatetime+"' ORDER BY id desc")
                        else :
                            cur1.execute("SELECT id,web,title,title_tw,publishdate,url,content FROM news_daily_source WHERE status=0 and content is not null and "+query_str+" and language='"+language+"' and creationdate>'"+subscribeUpdatetime+"' ORDER BY id desc")    

                        for r1 in cur1 :
                            #print(123)
                            newsid = r1[0]
                            publishdate = r1[4]
                            title = r1[2]+'  ['+str(publishdate)+']'
                            url = r1[5]
                            content = r1[6]+'\n'+url
                            #print(useraccount,apikey,team_sn,content,title,'\n\n')
                            result = mapp_team(useraccount,apikey,team_sn,content,title)
                            cur2.execute("insert into news_keyword_subscribe_log (subscribeid,newsidlist,useraccount,apikey,team_sn,creationdate, status,ErrorCode,IsSuccess,Description)values(%s,%s,%s,%s,%s,%s, %s,%s,%s,%s)",(subscribeid,newsid,useraccount,apikey,team_sn,creationdate, result[0],result[1],result[2],result[3]))
                            time.sleep(2) 
                        
                        
                    cur1.execute("update news_keyword_subscribe set updatetime=%s where id=%s",(creationdate,subscribeid))


                cur1.execute("COMMIT")
            except Exception as e:
                print(' === query_str ERROR!  id:',subscribeid,' , query_str:',query_str,' ',e)
                #break
                pass
            #print(id,'. PERNRList:',PERNRList,' len:',len(PERNRList),' , chatsnList:',chatsnList,' len:',len(chatsnList))
             
    cur.close()
    cur1.close()
    cur2.close()
    conn.close()
     
# 20210326
# 取得 + - | 的所有出現位子
def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

# 20210326
# 將關鍵字組轉成SQL where條件式
def convertKeywordToSQLStatement(keywordOrigin) :
    keywordList = re.split('\+|-|\|', keywordOrigin)
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
            if strLen > notIndex :
                keywordDict[keywordList[c]] = '-'
                break
            c = c + 1

    # OR        
    orList = findOccurrences(keywordOrigin, '|')
    for orIndex in orList : 
        strLen = 0
        c=1
        for keyw in keywordDict :
            strLen = strLen + len(keyw)+1 
            if strLen > orIndex :
                keywordDict[keywordList[c]] = '|'
                break
            c = c + 1 

    # 取得OR，並插入括弧
    beforeBoolean = ''
    c = 1
    orIndex = []
    for key in keywordDict:
        if beforeBoolean != '' and beforeBoolean != '|' and keywordDict[key] == '|' :        
            orIndex.append(c - 1)
            #print('orIndex 1')
        if beforeBoolean == '|' and keywordDict[key] != '|' :
            orIndex.append(c - 1)
            #print('orIndex 2')
        elif c > 1 and len(orIndex) > 0 and c == len(keywordDict) :
            orIndex.append(c)
            #print('orIndex 3')

        beforeBoolean = keywordDict[key]
        c = c + 1

    c = 1 
    for key in keywordDict:
        if keywordDict[key] == '+' :
            if c == 1 and c in orIndex :
                sqlWhereState = sqlWhereState+'(' 
            elif c == 1 and c not in orIndex :
                sqlWhereState = ' content like "%'+key.strip()+'%"'
            elif c != 1 and c in orIndex :
                sqlWhereState = sqlWhereState+' and ( content like "%'+key.strip()+'%"'
            else :    
                sqlWhereState = sqlWhereState+' and content like "%'+key.strip()+'%"'

        elif keywordDict[key] == '|' :
            sqlWhereState = sqlWhereState+' or content like "%'+key.strip()+'%"'
            if c in orIndex :
                sqlWhereState = sqlWhereState+')'    
        elif keywordDict[key] == '-' :
            sqlWhereState = sqlWhereState+' and content not like "%'+key.strip()+'%"'
        c = c + 1        
    #print(sqlWhereState)        
        
    return sqlWhereState   

def mappPERNR(PERNR,content) :
    timesleep = 10
    #print('mappPERNR',PERNR)
    if PERNR == '18017220':
        PERNR = 'API_SmartPush'
    option = webdriver.ChromeOptions() 
    option.add_argument("--disable-gpu"); 
    option.add_argument("--start-maximized");  
    option.add_argument('--headless')      
    
    driver = webdriver.Chrome(r"D:\chromedriver.exe",chrome_options=option)
    url = 'http://mapp.local/teamplus_innolux/'
    driver.get(url)
    
    time.sleep(timesleep)   

    # Step1.輸入帳密登入
    driver.find_element_by_name("txt_account").click()
    driver.find_element_by_name("txt_account").clear()
    driver.find_element_by_name("txt_account").send_keys(mappName)
    driver.find_element_by_name("txt_password").click()
    driver.find_element_by_name("txt_password").clear()
    driver.find_element_by_name("txt_password").send_keys(mappPW)
    #driver.execute_script("beforelogin();")
    driver.find_element_by_name("btn_login").click()

    # Step2.點左側清單=>即時交談
    driver.find_element_by_id("IdeskLMenu_3").click() 
    time.sleep(timesleep) 
    # Step3.點右上"+"，展開選單
    driver.find_element_by_class_name("chatOptionBtn").click()
    time.sleep(timesleep) 
    # Step4.點"新增交談"，開啟通訊錄
    driver.find_element_by_xpath('//*[@id="divPersonalLogSideBar"]/div[2]/div[2]/div[3]/ul/li[1]').click()
    time.sleep(timesleep) 

    # Step5.點搜尋框，輸入工號，並Enter搜尋
    driver.find_element_by_class_name("contentEditBox").click()
    driver.find_element_by_class_name("contentEditBox").send_keys(PERNR)
    driver.find_element_by_class_name("contentEditBox").send_keys(u'\ue007')
    time.sleep(timesleep*4) 

    # Step6.搜尋完點左上的"全選"
    driver.find_element_by_class_name("selectAllBtn").click()

    # Step7.點選右下"確定"
    driver.find_element_by_class_name("confirmSelectMemberBtn").click()
    time.sleep(timesleep) 

    # Step8.底下輸入內容並送出
    driver.find_element_by_class_name("contentEditBox").send_keys(content)    
    #driver.execute_script("document.getElementsByClassName('contentEditBox')[0].innerHTML='{}'".format(content));
    time.sleep(timesleep) 
    driver.find_element_by_class_name("contentEditBox").send_keys(u'\ue007')
    driver.close()
    #print('mappPERNR success!')    
    
def mappChatsn(chatsn,content) :
    conn = pymysql . connect ( host = host , port = port , user = user , passwd = passwd , db = db ) 
    cur = conn . cursor ()
    
    result = mapppost_content(useraccount,apikey,chatsn,content)
    return result
    
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
    result = json.loads(response.text)
                
    if not result['IsSuccess'] :
        return [3,result['ErrorCode'],result['IsSuccess'],result['Description']]
    
    return [0,result['ErrorCode'],result['IsSuccess'],result['Description']]

def mapp_team(useraccount,apikey,team_sn,content,subject) :
    
    #content = 'xxx工作事項'
    #useraccount = 'va_1f28300870404a5ea8' 
    #apikey = 'c4461d83-3170-4545-a27a-7fcd697f8920'
    #team_sn = '4538'
    #subject='subject subject subject subject subject'
    subject_utf8 = subject.encode("UTF-8")#轉UTF8
    subject_utf8_url = urllib.parse.quote_plus(subject_utf8)
    #print(useraccount,'\n',apikey,'\n',team_sn,'\n',content,'\n',subject)
    content_utf8 = content.encode("UTF-8")#轉UTF8
    content_utf8_url = urllib.parse.quote_plus(content_utf8)#轉URL
    url = "http://mapp.local/teamplus_innolux/API/TeamService.ashx"
    payload = "ask=postMessage&account={}&api_Key={}&team_sn={}&content_type=1&text_content={}&subject={}&media_content=&file_show_name=&undefined=".format(useraccount,apikey,team_sn,content_utf8_url,subject_utf8_url)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "c6a39fb6-cdd9-48e0-bc0e-9f35e3f5d147"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    result = json.loads(response.text)
    #print('mapp_team:', response.text)
    if not result['IsSuccess'] :
        return [3,result['ErrorCode'],result['IsSuccess'],result['Description']]
    
    return [0,result['ErrorCode'],result['IsSuccess'],result['Description']]

#get_subscribe_news()
scheduler = BlockingScheduler()  
scheduler.add_job(get_subscribe_news, 'cron', hour='*/1', minute='*/20') 
scheduler.start()