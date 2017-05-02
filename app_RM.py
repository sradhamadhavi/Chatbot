import os
import sys
import json
import requests
import nltk
import pymysql
# from nltk.tokenize import sent_tokenize,word_tokenize
#from chatterbot import ChatBot
from flask import Flask, request,jsonify
from nltk import ne_chunk,pos_tag
from sklearn.externals import joblib
import numpy as np
import spacy
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
token="EAACVPy7Oy2gBAF6HNoT1inoNFuK5DF49umuFLMPGmxjaQf6SiCPVecDKZCRFZAdi7FZAmiiSQXkUpCYkrhat9C23O2TZBUuGxUMU1BzSP37DtlpZAWtD4yhk70n2FHL4ftdgqldDOkWNCV43QNnXjy4j8UxZAZCVfNDxQvZBH5aHIAZDZD"
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

#import pymysql Postgres seems a better option.
clf = joblib.load('qa_clf.pkl') 
vect = joblib.load('vectorizer.pkl')
app = Flask(__name__)
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
# def getProductDetails(intent,entity):
#     conn=pymysql.connect(host='localhost',user='root',password='sparity@123',db='productdb')
#     a=conn.cursor()
#     sql="select  title,price from orgproddetails where title like '%"+entity+"%' LIMIT 5"
#     # if intent=='Price':
#     #     sql="select  title,price from orgproddetails where title like '%"+entity+"%' LIMIT 5"
#     # elif intent=='buy':
#     #     sql="select title,link from orgproddetails where title like '%"+entity+"%' LIMIT 5"
#     # elif intent=='Availability':
#     #     sql="select title,availability from orgproddetails where title like '%"+entity+"%' LIMIT 5"     
#     a.execute(sql)
#     countrow=a.execute(sql)
#     data=a.fetchall()
#     return  json.dumps(data)

##################################################################################################################################
def getProductDetails(sender,productTitle):
    log(productTitle)
    conn=pymysql.connect(host='localhost',user='root',password='sparity@123',db='productdb')
    cursor=conn.cursor()
    sql="select  description from productdb.orgproddetails where title = '"+productTitle+"'"
    # if intent=='Price':
    #     sql="select  title,price from orgproddetails where title like '%"+entity+"%' LIMIT 5"
    # elif intent=='buy':
    #     sql="select title,link from orgproddetails where title like '%"+entity+"%' LIMIT 5"
    # elif intent=='Availability':
    #     sql="select title,availability from orgproddetails where title like '%"+entity+"%' LIMIT 5"     
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
   # endpoint for processing incoming messaging events
    data = request.get_json()
    #log(data)  # you may not want to log every incoming message in production, but it's good for testing
    
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    log("inside message")
                    #log(messaging_event.get("message"))                    
                    # recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    #response = chatbot.get_response(message_text)
                    #response=getProductDetails(message_text)
                    #send_message(sender_id, intent)
                    if message_text.lower() == "hi" or message_text.lower() == "hello":
                        log(message_text.lower())
                        send_Textmessage(sender_id, "Hello, How can I help you?")
                        
                    else:
                        log(message_text.upper())
                        intent=getIntent(message_text)
                        entity=getEntity(message_text)
                        #entity='Boxer'
                        #send_message(sender_id, rowCount)
                        # rowCount=getProductCount(entity)
                        #if(rowCount>0):
                        #send_Textmessage(sender_id,"We have many products that matches your need. Can you choose from below list?")
                        #send_Textmessage(sender_id,getProductDetails(intent,entity))
                        #send_Textmessage(sender_id,intent)
                        try:
                            if entity.upper()=='TOPS':
                                send_Textmessage(sender_id,"We have range of collections in below categories. Please select the one you are intrested in.")
                                sendGenderForEntity(sender_id,entity.upper())
                            else:
                                send_Textmessage(sender_id,"I wish I could help you...")
                        except:
                            log(sys.exc_info()[0])
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
                        getData(sender_id,'TOPS_M')
                    elif message_text=='TOPS_F':
                        getData(sender_id,'TOPS_F')
                    else:
                        getProductDetails(sender_id,message_text)
          
           		
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
def getData(sender,Category):
    if Category=='TOPS_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('male') and title like '%T-Shirt%'limit 10"
    elif Category=='TOPS_F':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('female') and title like '%T-Shirt%'limit 10"
    elif Category=='BOTTOMS_F':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('female') and title like '%pant%'limit 10"
    elif Category=='BOTTOMS_M':
        dbQuery="SELECT * FROM productdb.orgproddetails where gender in ('male') and title like '%pant%'limit 10"
    
       
    conn=pymysql.connect(host='localhost',user='root',password='sparity@123',db='productdb')
    cursor=conn.cursor()    
    cursor.execute(dbQuery)
    rows=cursor.fetchall()
    i=0
    messageData="{\"attachment\": {\"type\": \"template\",\"payload\": {\"template_type\": \"generic\",\"elements\": [{"
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
	 
##################################################################################################################################
def QuickReply(sender):
    messageData={
        "text":"Pick a color:",
        "quick_replies":
        [
            {
                "content_type":"text",
                "title":"Red",
                "payload":"RED"
            },
            {
                "content_type":"text",
                "title":"Green",
                "payload":"GREEN"
            }
        ]
    }
    send_message(sender,messageData)
##################################################################################################################################
##################################################################################################################################
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')#,ssl_context=context)
