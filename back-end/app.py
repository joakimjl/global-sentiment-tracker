from flask import Flask
from flask import request

from data_form_querying import connect

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/info")
def hello_info():

    return fetch_sentiment()

def fetch_sentiment():
    

    try:
        country = request.args.get('country')
    except:
        country = "World"
    try:
        query = request.args.get('query')
    except:
        query = "Any"
    try:
        timeframe = request.args.get('timeframe')
    except:
        timeframe = 1
    
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT target_country,\
    sum(senti_count_nat[1]) as vader_nat,\
    sum(senti_count_nat[2]) as rober_nat,\
    sum(senti_count_int[1]) as vader_int,\
    sum(senti_count_int[2]) as rober_int\
    FROM global_info_hourly\
    GROUP BY target_country")
    return f"{cur.fetchall()}"