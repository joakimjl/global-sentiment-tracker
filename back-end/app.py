from flask import Flask
from flask import request
from data_form_querying import connect
from flask_cors import CORS, cross_origin

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
    print(request.remote_addr)
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

    return fetch_sentiment(country,query,timeframe)

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
    return f"{cur.fetchall()}"

if __name__ == "__main__":
    app.run(ssl_context='adhoc')