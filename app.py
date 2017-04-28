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
nlp = spacy.load('en')
import token_function
from  SpacyTraining_Products import predictEnt
# import os
# os.system('token_function.py')
import string
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer
import pandas as pd

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

clf = joblib.load('qa_clf.pkl') 
vect = joblib.load('vectorizer.pkl')
app = Flask(__name__)
#This is to train the model with English corpus
# chatbot = ChatBot(
#                     'RChat',
#                     trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
#                     )
# chatbot.train("chatterbot.corpus.english")

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200

@app.route('/get/<string:prod>',methods=['GET'])
def get_raw_response(prod):
    #return str(chatbot.get_response(query))
    #uri="http://localhost:8080/prod/1234"#+prod_id
    #res=getProductDetails(prod)
    intent=getIntent('I want to buy a Blanket')
    entity=getEntity('I want to buy a Blanket')
    res=getProductDetails(intent,entity)
    return res
    
def getProductDetails(intent,entity):
    conn=pymysql.connect(host='kaushal',user='dbuser',password='Tesco@123',db='productdb')
    a=conn.cursor()
    sql="select title,price from orgproddetails where title like '%"+entity+"%'"
    a.execute(sql)
    countrow=a.execute(sql)
    data=a.fetchall()
    return  json.dumps(data)
    
def getIntent(query):
    X_test = np.array([query])
    X_t = vect.transform(X_test)
    # feature_names = vect.get_feature_names()
    # for token in X_t.nonzero()[1]:
    #     return (feature_names[token], ' - ', X_t[0, token])
    pred = clf.predict(X_t)
    return pred[0]  

def getEntity(query):
   ent=predictEnt(query)
   return ent


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    #log(data["object"]) # you may not want to log every incoming message in production, but it's good for testing
    intent=getIntent(data["message"])
    entity=getEntity(data["message"])
    res="Intent "+intent+" "+str(entity)
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    #response = chatbot.get_response(message_text)
                    #response=getProductDetails(message_text)
                    if message_text=="Hi":
                        send_message(sender_id, "Hello, How can I help you?")
                    else:
                        send_message(sender_id, getIntent(message_text))

                    send_message(sender_id, getIntent)
                    send_message(sender_id, "Thanks For your message, we will get back to you at the earliest")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
    else:
        sender_id = messaging_event["sender"]["id"] 
        send_message(sender_id, "Thanks For your message, we will get back to you at the earliest")
    return res, 200    
def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print (str(message))
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
