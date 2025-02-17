from flask import Flask
from flask import request
from data_form_querying import connect
from flask_cors import CORS, cross_origin
import json
from country_codes import country_codes_map
import datetime as datetime
import nltk

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods=["GET"])
@cross_origin()
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/info", methods=["GET"])
@cross_origin()
def hello_info():
    try:
        country_code = request.headers.get('country')
        country = next(key for key, value in country_codes_map.items() if value == country_code)
    except:
        country = "World"
    try:
        query = request.headers.get('query')
    except:
        query = "Any"
    try:
        timeframe = request.headers.get('timeframe')
    except:
        timeframe = 1

    return fetch_sentiment_timeframe(country,query,timeframe)

def fetch_sentiment_timeframe(country,query,timeframe):
    conn = connect()
    cur = conn.cursor()
    country = str(country)
    query = str(query)
    timeframe = int(timeframe)
    if (country != "World"):
        cur.execute("SELECT target_country,\
        sum(senti_count_nat[1]) as vader_nat,\
        sum(senti_count_nat[2]) as rober_nat,\
        sum(senti_count_int[1]) as vader_int,\
        sum(senti_count_int[2]) as rober_int,\
        on_time \
        FROM global_info_hourly \
        WHERE target_country = %s AND target_country != %s\
        GROUP BY target_country, on_time",(str(country),"none"))
    else:
        cur.execute("SELECT target_country,\
        sum(senti_count_nat[1]) as vader_nat,\
        sum(senti_count_nat[2]) as rober_nat,\
        sum(senti_count_int[1]) as vader_int,\
        sum(senti_count_int[2]) as rober_int,\
        on_time \
        FROM global_info_hourly \
        GROUP BY target_country, on_time")
    res = cur.fetchall()
    temp_res = []
    for ele in res:
        temp = [country_codes_map[ele[0]],ele[1],ele[2],ele[3],ele[4],ele[5].strftime("%Y-%m-%d-%H"),ele[0]]
        temp_res.append(temp)
    #Data format is country, vader national, roberta national, vader international, roberta international
    return json.dumps(temp_res)

def fetch_sentiment(country,query,timeframe):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT target_country,\
    sum(senti_count_nat[1]) as vader_nat,\
    sum(senti_count_nat[2]) as rober_nat,\
    sum(senti_count_int[1]) as vader_int,\
    sum(senti_count_int[2]) as rober_int\
    FROM global_info_hourly\
    GROUP BY target_country")
    res = cur.fetchall()
    temp_res = []
    for ele in res:
        temp = [country_codes_map[ele[0]],ele[1],ele[2],ele[3],ele[4],ele[0]]
        temp_res.append(temp)
    #Data format is country, vader national, roberta national, vader international, roberta international
    return json.dumps(temp_res)

@app.route("/word_info", methods=["GET"])
@cross_origin()
def fetch_word_data():
    try:
        country_code = request.headers.get('country')
        country = next(key for key, value in country_codes_map.items() if value == country_code)
    except:
        country = "World"
    try:
        day = request.headers.get('day')
    except:
        day = "Any"

    conn = connect()
    cur = conn.cursor()
    country = str(country)
    try:
        day = datetime.datetime.strptime(day, "%Y-%m-%d-%H")
    except:
        print(day)

    dayAfter = day+datetime.timedelta(days=1)

    cur.execute("SELECT\
    on_time, \
    UNNEST(headline_inter), \
    UNNEST(sentiment_inter[2:2]) as bert \
    FROM global_info_hourly \
    WHERE target_country = %s AND on_time >= %s AND on_time <= %s\
    GROUP BY target_country, on_time, headline_inter, sentiment_count_res",(str(country),day,dayAfter))
    
    res = cur.fetchall()
    temp_res = []
    for ele in res:
        temp_arr = []
        temp_arr.append(ele[0].strftime("%Y-%m-%d-%H"))
        temp_arr.append(ele[1])
        temp_arr.append(ele[2])
        temp_res.append(temp_arr)
    resWords = impact_words(json.dumps([temp_res]))
    return json.dumps(resWords)


def impact_words(jsonInfo):
    loadJson = json.loads(jsonInfo)
    loadJson = loadJson[0]
    allWords = {}

    tokenizer = nltk.NLTKWordTokenizer()

    for i in range(len(loadJson)):
        stringFix = "[" + loadJson[i][2][1:-1] + "]"
        sentiment = json.loads(stringFix)[2] - json.loads(stringFix)[0]
        processed = loadJson[i][1].split('"')
        sentence = tokenizer.tokenize(processed[1])

        for pair in nltk.pos_tag(sentence):
            if pair[1] == "NNP" and len(pair[0]) >= 2:
                if allWords.get(pair[0]) == None:   
                    allWords[pair[0]] = [1,sentiment]
                else:
                    allWords[pair[0]][0] += 1
                    allWords[pair[0]][1] += sentiment

    allWords = {k: v for k, v in sorted(allWords.items(), key=lambda item: item[1][1])}

    posWords = []
    negWords = []

    i = 0

    for ele in allWords:
        if i < 8:
            posWords.append([ele, allWords[ele]])
        if i+8 >= len(allWords):
            negWords.append([ele, allWords[ele]])
        i+=1
    print(negWords)
    print(posWords)
    return[posWords,negWords]


def create_server():
    return app

if __name__ == "__main__":
    app.run(ssl_context='adhoc')
