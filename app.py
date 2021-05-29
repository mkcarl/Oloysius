#! ..\venv\scripts\python.exe
from os import write
from typing import Type
from flask import Flask, redirect, url_for, render_template, session, request
import json
from py2neo import Graph
from intents import return_fulfillment


app = Flask(__name__)
app.secret_key = "idkmen"

@app.route("/")
def home(): 
    return render_template("index.html")

# webhook 
@app.route("/webhook", methods=["POST"])
def webhook(): 
    data = request.get_json(silent=True)
    with open("data.json", "w") as f: 
        json.dump(data, f)
    return return_fulfillment(data)




if __name__ == "__main__": 
    app.run(debug=True, port=8080, host="0.0.0.0")
