from flask import Flask

from data_form_querying import connect

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/info")
def hello_world():
    return "<p>Hello, info!</p>"