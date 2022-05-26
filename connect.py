from flask import Flask
import requests
from flask_cors import CORS
from flask import request
import nltk
import wget
import numpy as np
import re
import os  # Regular expressions
import random
import string  # to process standard python strings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import wget
import random
import string
import re, string, unicodedata
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
import wikipedia as wk
from collections import defaultdict
import warnings

warnings.filterwarnings("ignore")
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel


app = Flask(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route("/")
def status():
    return random.choice(["Hey Talk to me!","I miss you!","Feeling Bored","I am excited","Its raining Today :(","My master Susheel trained me!","I know I am The Best","Waiting for you to speak... :|"])

# To get google docs data into txt file
def getFromGoogleDocs():
    url = "https://docs.google.com/feeds/download/documents/export/Export?id=19Qf_oXh2m8k1oEQNgz6hjBPp-JoXc01G&exportFormat=txt"
    #os.remove("/app/chatbot.txt")
    wget.download(url, out="chatbot.txt")

# To normalize text
def Normalize(text):
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    # word tokenization
    word_token = nltk.word_tokenize(text.lower().translate(remove_punct_dict))

    # remove ascii
    new_words = []
    for word in word_token:
        new_word = (
            unicodedata.normalize("NFKD", word)
            .encode("ascii", "ignore")
            .decode("utf-8", "ignore")
        )
        new_words.append(new_word)

    # Remove tags
    rmv = []
    for w in new_words:
        text = re.sub("&lt;/?.*?&gt;", "&lt;&gt;", w)
        rmv.append(text)

    # pos tagging and lemmatization
    tag_map = defaultdict(lambda: wn.NOUN)
    tag_map["J"] = wn.ADJ
    tag_map["V"] = wn.VERB
    tag_map["R"] = wn.ADV
    lmtzr = WordNetLemmatizer()
    lemma_list = []
    rmv = [i for i in rmv if i]
    for token, tag in nltk.pos_tag(rmv):
        lemma = lmtzr.lemmatize(token, tag_map[tag[0]])
        lemma_list.append(lemma)
    return lemma_list

# Variables

# getFromGoogleDocs()
cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in here %r: %s" % (cwd, files))
f = open("chatbot.txt", "r", errors="ignore")
raw = f.read()
raw = raw.lower()  # converts to lowercase
raw = re.sub("\________________+", "", raw)
raw = re.sub("\s+", " ", raw)
raw = re.sub("\d\.+", "", raw)


sent_tokens = nltk.sent_tokenize(raw)
welcome_input = (
    "hello",
    "hi",
    "greetings",
    "sup",
    "what's up",
    "hey",
)
welcome_response = [
    "hi",
    "hey",
    "*nods*",
    "hi there",
    "hello",
    "I am glad! You are talking to me",
]


def welcome(user_response):
    for word in user_response.split():
        if word.lower() in welcome_input:
            return random.choice(welcome_response)


def generateResponse(user_response):
    robo_response = ""
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=Normalize, stop_words="english")
    tfidf = TfidfVec.fit_transform(sent_tokens)
    # vals = cosine_similarity(tfidf[-1], tfidf)
    vals = linear_kernel(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if (req_tfidf == 0) or "tell me about" in user_response:
        print("Checking Wikipedia")
        if user_response:
            robo_response = wikipedia_data(user_response)
            return robo_response
    else:
        robo_response = robo_response + sent_tokens[idx]
        return robo_response


def wikipedia_data(input):
    reg_ex = re.search("(.*)", input)
    try:
        if reg_ex:
            topic = reg_ex.group(1)
            wiki = wk.summary(topic, sentences=3)
            return "Wikipedia says... "+wiki
    except Exception as e:
        return "Oops! My master Susheel didn't train me for this"






@app.route("/reply", methods=["POST"])
def reply():
    request_data = request.get_json()
    user_response = request_data["message"]
    flag = True
    print("My name is Chatterbot and I'm a chatbot. If you want to exit, type Bye!")
    while flag == True:
        # user_response = input()
        user_response = user_response.lower()
        if user_response not in ["bye", "shutdown", "exit", "quit"]:
            if user_response == "thanks" or user_response == "thank you":
                flag = True
                return "You are welcome.."
            else:
                if welcome(user_response) != None:
                    return " " + welcome(user_response)
                else:
                    return generateResponse(user_response)
                    sent_tokens.remove(user_response)
        else:
            flag = True
            return " Bye!!! "


if __name__ == "__main__":
    app.run(debug=True)
