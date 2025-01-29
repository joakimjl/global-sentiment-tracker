from flask import Flask

from data_form_querying import connect

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/info")
def hello_info():
    conn = connect()
    cur = conn.cursor()
    print("Executing")
    cur.execute("SELECT * FROM global_info_hourly")
    print(cur.fetchone())
    return (cur.fetchone())