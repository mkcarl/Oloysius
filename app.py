#! .\venv\scripts\python.exe
from flask import Flask, redirect, url_for, render_template, session


app = Flask(__name__)
app.secret_key = "idkmen"


@app.route("/")
def home(): 
    return render_template("index.html")

# webhook 
@app.route("/webhook", methods=["POST"])
def webhook(): 
    
    
    return 


if __name__ == "__main__": 
    app.run(debug=True)
