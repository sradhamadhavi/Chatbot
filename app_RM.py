import os
import sys
import json
import requests
import nltk
import pymysql
# from nltk.tokenize import sent_tokenize,word_tokenize
#from chatterbot import ChatBot
from flask import Flask, request,jsonify,_request_ctx_stack,current_app,has_request_context
from nltk import ne_chunk,pos_tag
from sklearn.externals import joblib
import numpy as np
import spacy
app=Flask(__name__)
i=1

# import token_function
#from OpenSSL import SSL
#context=('host.cert','host.key')
nlp = spacy.load('en',parser=False)
from  SpacyTraining_Products import predictEnt
import string
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer
import pandas as pd
token="EAACVPy7Oy2gBAJrDRYkKzjUfcE8VCaV8DG3m9dKxpnoIwZBVoBuIYkWQkJK7xhWOXjt7i0pPDc9xfWlYypj85xPnopUBJjFcH7gpYJdmNLnk02vaVX9ZBkl2TZBz4ns4qrReNb4NSGpnZCyTyufO6z7eaILpgmtxzXmS6yO7rgZDZD"
url="https://graph.facebook.com/v2.6/me/messages"


#from messengerbot import messenger

stemmer = PorterStemmer()
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    text = "".join([ch for ch in text if ch not in string.punctuation])
    tokens = word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

# def get_session():
#     ctx =  app.app_context()
#     log("inside Session")
#     try:
#         # ctx.push()
#         log(current_app.name)
#         print(ctx)
#     except:
#         log(sys.exc_info()[0])
#     # if has_request_context():
#     #     log("inside if")
        
#     if ctx is not None:
#         sampObj=ctx.pop()
#         print(sampObj)

#import pymysql Postgres seems a better option.
clf = joblib.load('qa_clf.pkl') 
vect = joblib.load('vectorizer.pkl')
#app = Flask(__name__)
#This is to train the model with English corpus
# chatbot = ChatBot(
#                     'RChat',
#                     trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
#                     )
# chatbot.train("chatterbot.corpus.english")
##################################################################################################################################
@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "12345":#os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200
##################################################################################################################################
@app.route('/get/<string:prod>',methods=['GET'])
def get_raw_response(prod):
    res=getIntent('What is the Price?')
    return (res)
##################################################################################################################################   


##################################################################################################################################
def getProductDetails(sender,productTitle):
    log(productTitle)
    conn=pymysql.connect(host='localhost',user='root',password='sparity@123',db='productdb')
    cursor=conn.cursor()
    sql="select  description from productdb.orgproddetails where title = '"+productTitle+"'"
    cursor.execute(sql)
    data=cursor.fetchone()
    send_Textmessage(sender,data[0])
##################################################################################################################################
def getIntent(query):
    X_test = np.array([query])
    X_t = vect.transform(X_test)
    # feature_names = vect.get_feature_names()
    # for token in X_t.nonzero()[1]:
    #     return (feature_names[token], ' - ', X_t[0, token])
    pred = clf.predict(X_t)
    return pred[0]  
 ##################################################################################################################################   
def getEntity(query):
   ent=predictEnt(query)
   return ent
##################################################################################################################################
def getProductCount(entity):
    conn=pymysql.connect(host='localhost',user='root',password='sparity@123',db='productdb')
    a=conn.cursor()
    sql="select count(*)  from orgproddetails where title like '%"+entity+"%'"
    a.execute(sql)
    countrow=a.fetchall()
    return countrow

##################################################################################################################################
@app.route('/', methods=['POST'])
def webhook():
    global categorySaved
    # global itemCount
   # endpoint for processing incoming messaging events
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing
    
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]  # the message's text
                    if message_text.lower() == "hi" or message_text.lower() == "hello":
                        send_Textmessage(sender_id, "Hello, How can I help you?")
                        QuickReply(sender_id)
                        log(message_text)
                        # get_session()
                    elif message_text=='Men':
                        # itemCount=0
                        sendMale_Category(sender_id)
                    elif message_text== 'Women':
                        # itemCount=0
                        sendFem_Category(sender_id)
                    elif message_text== 'Kids':
                        # itemCount=0
                        sendKids_Category(sender_id)
                    elif message_text== 'Accessories':
                        sendAcc_Category(sender_id)
                    elif message_text== 'Blankets':
                        getData(sender_id,'Blankets','')
                    elif message_text=='Yes' and categorySaved== 'TOPS_M':
                        getData(sender_id,'TOPS_M',categorySaved)#,itemCount+10)
                    elif message_text=='Yes' and categorySaved== 'TOPS_F':
                        getData(sender_id,"TOPS_F",categorySaved)
                    elif message_text=='Yes' and categorySaved== 'BOTTOMS_M':
                        getData(sender_id,"BOTTOMS_M",categorySaved)
                    elif message_text=='Yes' and categorySaved== 'BOTTOMS_M':
                        getData(sender_id,"BOTTOMS_M",categorySaved)
                    elif message_text=='Yes' and categorySaved== 'BOTTOMS_F':
                        getData(sender_id,"BOTTOMS_F",categorySaved)
                    elif message_text=='Yes' and categorySaved=='LOUNGE+SLEEPWEAR_M':
                        getData(sender_id,"LOUNGE+SLEEPWEAR_M",categorySaved)
                        
                    elif message_text== 'No':
                        send_Textmessage(sender_id,"Do you wish to start over again?")
                        QuickReply(sender_id)
                        


                    else:
                        intent=getIntent(message_text)
                        entity=getEntity(message_text)
                        log(entity)
                        if  entity:
                            try:
                                if entity.upper()=='TOPS':
                                    send_Textmessage(sender_id,"We have range of collections in below categories. Please select the one you are intrested in.")
                                    sendGenderForEntity(sender_id,entity.upper())
                                elif entity.upper()=='BOTTOMS':
                                    send_Textmessage(sender_id,"Cool...gimme more info so that I can help you better")
                                    sendGenderForEntity(sender_id,entity.upper())
                                elif entity.upper()=='TSHIRTS':
                                    send_Textmessage(sender_id,"Superb... tell me which category you are looking at ")
                                    sendGenderForEntity(sender_id,entity.upper())
                                else:
                                    send_Textmessage(sender_id,"I wish I could help you...")
                            except:
                                log(sys.exc_info()[0])
                        else:
                            send_Textmessage(sender_id,"Sorry, Could not understand")
                    # else:
                    #     send_message(sender_id,getProductDetails(price,message_text))
                elif messaging_event.get("postback"):
                    message_text = messaging_event["postback"]["payload"]
                    log("inside postback")
                    if message_text=="START_OVER" or message_text=='MAIN_MENU':
                        sendMainMenu_Gender(sender_id)
                    elif message_text=='MALE':
                        sendMale_Category(sender_id)
                    elif message_text== 'FEMALE':
                        sendFem_Category(sender_id)
                    elif message_text== 'KIDS':
                        sendKids_Category(sender_id)
                    elif message_text=='TOPS_M':
                        categorySaved='TOPS_M'
                        getData(sender_id,'TOPS_M','')
                    elif message_text=='TOPS_F':
                        categorySaved='TOPS_F'
                        getData(sender_id,'TOPS_F','')
                    elif message_text=='BOTTOMS_F':
                        categorySaved='BOTTOMS_F'
                        getData(sender_id,'BOTTOMS_F','')
                    elif message_text=='BOTTOMS_M':
                        categorySaved='BOTTOMS_M'
                        getData(sender_id,'BOTTOMS_M','')
                    elif message_text=='TSHIRTS_M':
                        getData(sender_id,'TSHIRTS_M','')
                    elif message_text=='TSHIRTS_F':
                        getData(sender_id,'TSHIRTS_F','')
                    elif message_text=='LOUNGE+SLEEPWEAR_M':
                        categorySaved='LOUNGE+SLEEPWEAR_M'
                        getData(sender_id,'LOUNGE+SLEEPWEAR_M','')
                        
                    else:
                        getProductDetails(sender_id,message_text)
                
                elif messaging_event.get("quickreply"):
                    log("inside quickreply")
          
           		
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

               

    return "ok", 200

##################################################################################################################################
def send_message(recipient_id, message_text):
    #log("sending message1 to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    #log(message_text)
    params = {"access_token":token}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message":  message_text
        
    })
    r = requests.post(url, params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
##################################################################################################################################
def send_Textmessage(recipient_id, message_text):
    #log("sending message1 to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    #log(message_text)
    params = {"access_token":token}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    })
    r = requests.post(url, params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
##################################################################################################################################

def log(message):  # simple wrapper for logging to stdout on heroku
    print (str(message))
    sys.stdout.flush()
##################################################################################################################################
def sendMessageSample(sender,text):
    recipient = messages.Recipient(sender)
    # Send text message
    message = messages.Message(text=text)
    request = messages.MessageRequest(sender, message)
    messenger.send(request)
##################################################################################################################################
def sendMainMenu_Gender(sender):
    messageData = {
        "attachment":{
        "type":"template",
        "payload":{
            "template_type":"button",
            "text":"Choose Category",
            "buttons":[
            {
                "type":"postback",
                "title":"Men",
                "payload":"MALE"
            },
            {
                "type":"postback",
                "title":"Women",
                "payload":"FEMALE"
            }, 
            {
                "type":"postback",
                "title":"Kids",
                "payload":"KIDS"
            }
            ]
        }
        }
    }
    send_message(sender,messageData)
##################################################################################################################################
def sendGenderForEntity(sender_id,entity):
    messageData = "{"
    messageData= messageData+  "\"attachment\":{"
    messageData= messageData+    "\"type\":\"template\","
    messageData= messageData+    "\"payload\":{"
    messageData= messageData+        "\"template_type\":\"button\","
    messageData= messageData+        "\"text\":\"Choose Category\","
    messageData= messageData+        "\"buttons\":["
    messageData= messageData+            "{"
    messageData= messageData+            "\"type\":\"postback\","
    messageData= messageData+            "\"title\":\"Men\","
    messageData= messageData+            "\"payload\":\""+entity+"_M\""
    messageData= messageData+        "},"
    messageData= messageData+        "{"
    messageData= messageData+            "\"type\":\"postback\","
    messageData= messageData+            "\"title\":\"Women\","
    messageData= messageData+            "\"payload\":\""+entity+"_F\""
    messageData= messageData+        "},"
    messageData= messageData+        "{"
    messageData= messageData+            "\"type\":\"postback\","
    messageData= messageData+            "\"title\":\"Kids\","
    messageData= messageData+            "\"payload\":\""+entity+"_KIDS\""
    messageData= messageData+        "}"
    messageData= messageData+        "]"
    messageData= messageData+    "}"
    messageData= messageData+    "}"
    messageData= messageData+"}"
    send_message(sender_id,messageData)
##################################################################################################################################
def sendMale_Category(sender):
    messageData = {
        "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":"Choose Category",
                "buttons":[
                    {
                        "type":"postback",
                        "title":"Tops",
                        "payload":"TOPS_M"
                    },
                    {
                        "type":"postback",
                        "title":"Bottoms",
                        "payload":"BOTTOMS_M"
                    },
                    {
                        "type":"postback",
                        "title":"Lounge + Sleepwear",
                        "payload":"LOUNGE+SLEEPWEAR_M"
                    }
                ]
            } 
        }
    }
    send_message(sender,messageData)
##################################################################################################################################
def sendKids_Category(sender):
    messageData = {
        "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":"Choose Category",
                "buttons":[
                    {
                        "type":"postback",
                        "title":"Boys",
                        "payload":"BOYS"
                    },
                    {
                        "type":"postback",
                        "title":"Girls",
                        "payload":"GIRLS"
                    },
                    {
                        "type":"postback",
                        "title":"Infants",
                        "payload":"INFANTS"
                    }
                ]
            }
        }
    }
    send_message(sender,messageData)
##################################################################################################################################
def sendFem_Category(sender):
    messageData = {
        "attachment":{
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":"Choose Category",
                "buttons":[
                    {
                        "type":"postback",
                        "title":"Tops",
                        "payload":"TOPS_F"
                    },
                    {
                        "type":"postback",
                        "title":"Bottoms",
                        "payload":"BOTTOMS_F"
                    },
                    {
                        "type":"postback",
                        "title":"Lounge + Sleepwear / BSport Active",
                        "payload":"LOUNGE+SLEEPWEAR_F+BSPORT"
                    }
                ]
            }
        }
    }
    send_message(sender,messageData)
##################################################################################################################################
def sendAcc_Category(sender):
    messageData={
            "text":"Accessories definitely enhance the looks.Here are some",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Blankets",
                "payload":"BLANKETS"
            }
            ]  
    }
    send_message(sender,messageData)


##################################################################################################################################
def getData(sender,Category,categorySaved):
    # send_Textmessage(sender,Category+" "+categorySaved)
    if Category=='TOPS_M' and categorySaved=='TOPS_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('male') and title like '%T-Shirt%'  order by rand()  limit 5,10"
    elif Category=='TOPS_F' and categorySaved=='TOPS_F':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('female') and title like '%T-Shirt%' order by rand() limit 5,10"
    
    elif Category=='BOTTOMS_F'  and categorySaved=='BOTTOMS_F':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('female') and title like '%pant%' order by rand() limit 10,10"
    elif Category=='BOTTOMS_F':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('female') and title like '%pant%'limit 10"
    
    elif Category=='BOTTOMS_M' and categorySaved=='BOTTOMS_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('male') and title like '%pant%' order by rand() limit 10,10"
    elif Category=='BOTTOMS_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('male') and title like '%pant%'limit 10"
    elif Category=='LOUNGE+SLEEPWEAR_M' and categorySaved=='LOUNGE+SLEEPWEAR_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where  gender in ('male')and title like '%short%' order by rand() limit 5,5"
    elif Category=='LOUNGE+SLEEPWEAR_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where  gender in ('male')and title like '%short%' limit 5"
    
    elif Category=='TSHIRTS_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('male','unisex') and title like '%t-shirt%'limit 10"
    elif Category=='TSHIRTS_F':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('female','unisex') and title like '%t-shirt%'limit 10"
    elif Category=='TOPS_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('male') and title like '%T-Shirt%' order by rand() limit 5"
    elif Category=='TOPS_F':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('female') and title like '%T-Shirt%' order by rand() limit 5"
    elif Category=='Blankets':
        dbQuery="SELECT * FROM productdb.orgproddetails where  title like '%blanket%' limit 10"
    
       
    conn=pymysql.connect(host='localhost',user='root',password='sparity@123',db='productdb')
    cursor=conn.cursor()    
    cursor.execute(dbQuery)
    rows=cursor.fetchall()
    i=0
    messageData="{\"attachment\": {\"type\": \"template\",\"payload\": {\"template_type\": \"generic\",\"image_aspect_ratio\":\"square\",\"elements\": [{"
    for row in rows:
        i=i+1
        messageData+="\"title\": \""+row[2]+"\",\"image_url\": \""+row[5]
        messageData+="\",\"buttons\": [{\"type\": \"web_url\",\"url\": \""+row[4]+"\",\"title\": \"Click here to Buy\""
        messageData+="}, {\"type\": \"postback\",\"title\": \"More Details\",\"payload\": \""+row[2]+"\",}],}"
        if i==cursor.rowcount:
            messageData+="] } }  }"
        else:
            messageData+=", {"
    cursor.close()
    conn.close()    
    send_message(sender,messageData)
    ShowMore(sender)	 
##################################################################################################################################
def QuickReply(sender):
    messageData={
            "text":"Shopping is Awesome. Browse through some of our collections",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Men",
                "payload":"MALE"
            },
            {
                "content_type":"text",
                "title":"Women",
                "payload":"FEMALE"
            }, 
            {
                "content_type":"text",
                "title":"Kids",
                "payload":"KIDS"
            },
	        {
                "content_type":"text",
                "title":"Accessories",
                "payload":"ACCESSORIES"
            }
            ]  
    }
    send_message(sender,messageData)
##################################################################################################################################
def ShowMore(sender):
    messageData={
            "text":"Do you want to view more..?",
            "quick_replies":[
            {
                "content_type":"text",
                "title":"Yes",
                "payload":"YES"
            },
            {
                "content_type":"text",
                "title":"No",
                "payload":"NO"
            }
            ]  
    }
    send_message(sender,messageData)
##################################################################################################################################
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')#,ssl_context=context)
