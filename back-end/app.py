from flask import Flask
from flask import request
from data_form_querying import connect
from flask_cors import CORS, cross_origin
import json
from country_codes import country_codes_map

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
        country = request.headers.get('country')
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
        temp = [country_codes_map[ele[0]],ele[1],ele[2],ele[3],ele[4],ele[5].strftime("%Y-%m-%d-%H")]
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
        temp = [country_codes_map[ele[0]],ele[1],ele[2],ele[3],ele[4]]
        temp_res.append(temp)
    #Data format is country, vader national, roberta national, vader international, roberta international
    return json.dumps(temp_res)

def create_server():
    return app

if __name__ == "__main__":
    app.run(ssl_context='adhoc')